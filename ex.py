from functools import partial
import json
from py2neo import Graph, Path, GraphError
from os import getenv, path
import sys
from subprocess import Popen, PIPE
import logging

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler())


def clean_graph(graph):
    LOG.info('Cleaning up graph...')
    try:
        graph.cypher.execute('MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r')
        graph.schema.drop_uniqueness_constraint('Package', 'name')
    except GraphError as error:
        LOG.error('Problem cleaning up graph %r', error)


def get_graph(cleanup=False):
    uri = getenv('NEO4J_URI', 'http://neo4j:neo@localhost:7474/db/data/')
    LOG.info('Connecting to graph at: %s', uri)
    graph = Graph(uri)
    if cleanup:
        clean_graph(graph)
    try:
        graph.schema.create_uniqueness_constraint('Package', 'name')
    except GraphError as error:
        LOG.error(
            'Unable to create constrains (they already exist perhaps?) %r',
            error)
        return None

    return graph


def process_package(graph, package):
    deps = package.pop('depends')
    p = graph.merge_one('Package', 'name', package['name'])
    p.set_properties(package)
    if deps == "":
        return

    for dep in deps.split(','):
        dep_name = dep.split()[0]
        if dep_name is None:
            continue
        dep = graph.merge_one('Package', 'name', dep_name)
        LOG.info('(%s)-[:DEPENDS_ON]->(%s)', package['name'], dep_name)
        graph.create_unique(Path(p, 'DEPENDS_ON', dep))


def parse_package_list(package_list):
    ret = []
    for l in package_list:
        try:
            ret.append(json.loads(l))
        except ValueError as inst:
            LOG.error('Error processing %s %s', l, inst)
    return ret


def get_packages_from_file(fname):
    with open(fname, 'r') as f:
        return parse_package_list(f)


def generate_package_list():
    output_format = '{"status": "${Status}",' \
                    '"name": "${binary:Package}",' \
                    '"version": "${Version}", ' \
                    '"size": ${Installed-Size}, ' \
                    '"depends": "${Depends}"}\n'

    command = ['dpkg-query', '-W', '-f=%s' % output_format]
    process = Popen(command, stdout=PIPE)
    out, err = process.communicate()
    if err:
        LOG.error('Unable to execute command %s [error=%s] %s',
                  command, err, out)
    else:
        return parse_package_list(out.splitlines())


if __name__ == "__main__":
    fname = 'out.json'
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    if path.isfile(fname):
        LOG.info('Retrieving package list from %s', fname)
        packages = get_packages_from_file(fname)
    else:
        LOG.info('Generating package list with dpkg-query')
        packages = generate_package_list()

    if packages is None or len(packages) == 0:
        LOG.error('Unable to create package list')
        exit(-1)

    LOG.info('Got %d packages', len(packages))
    g = get_graph(cleanup=False) or exit(-1)
    map(partial(process_package, g), packages)
    g.push()
