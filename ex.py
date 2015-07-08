import json


def get_packages_list(f):
    packages = []
    for l in f:
        try:
            packages.append(json.loads(l))
        except Exception as inst:
            print 'Error processing %s %s' % (l, inst)

    return packages


if __name__ == "__main__":
    # read file generated with:
    #   dpkg-query -W -f='{"status": "${Status}", "name": "${binary:Package}",
    # "version": "${Version}", "size": ${Installed-Size}, "depends": "${
    # Depends}"}\n' > out.json
    with open('out.json', 'r') as f:
        packages = get_packages_list(f)
