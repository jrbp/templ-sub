#!/usr/bin/env python3

import sys
import os
import re
from glob import iglob
from copy import deepcopy

def get_templ_files(tdir, ignore=None):
    """ obtain list of files in tdir (including those inside other directories) """
    templ_files = []
    for fn in iglob(tdir + '/**/*', recursive=True):
        if not os.path.isdir(fn):
            templ_files.append(os.path.relpath(fn, tdir))
    return templ_files

def sub_file(tfile, subs):
    """ return string where substitutions have been made in tfile """
    with open(tfile) as f:
        file_string = f.read()
    for key, val in subs.items():
        file_string = re.sub('\!SUB{}SUB\!'.format(key), str(val), file_string)
    return file_string

def get_sub_set_from_templ(tdir):
    """ return a set of substitution keys in template directory tdir
        note: this will not find substitution keys with whitespace in them """
    subs = []
    for tfile in get_templ_files(tdir):
        with open(os.path.join(tdir, tfile)) as f:
            file_string = f.read()
        matches= re.findall('\!SUB(\S*)SUB\!', file_string)
        subs.extend(matches)
    return set(subs)

def replace_all_subs(tdir, ddir, c_subs, o_subs, prefix=None):
    """
    created new files in ddir from those in tdir with specified substitutions

    ARGS:
        tdir: template directory
        ddir: destination directory
        c_subs: common substitutions for all as a dict
        o_subs: list of specific substitutions which overwrite c_subs for that dest
        prefix: optional prefix arg for substituted dirs
    """

    if prefix is None:
        prefix = 'run_'

    tfiles = get_templ_files(tdir)

    for i, osub in enumerate(o_subs):
        dest = os.path.join(ddir, '{}{}'.format(prefix, i))

        subs = deepcopy(c_subs)
        subs.update(osub)

        for tfile in tfiles:
            d_file = os.path.join(dest, tfile)
            t_file_full = os.path.join(tdir, tfile)
            os.makedirs(os.path.dirname(d_file), exist_ok=True)
            new_file_str = sub_file(t_file_full, subs)
            with open(d_file, 'w') as f:
                f.write(new_file_str)
    return

if __name__ == '__main__':
    tdir = sys.argv[1]
    ddir = sys.argv[2]
    common_subs = json.load(sys.argv[3])
    ovr_subs = json.load(sys.argv[4])
    replace_all_subs(tdir, ddir, common_subs, ovr_subs)
