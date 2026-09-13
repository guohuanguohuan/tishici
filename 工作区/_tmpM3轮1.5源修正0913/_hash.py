# -*- coding: utf-8 -*-
import hashlib, sys, os
for p in sys.argv[1:]:
    b = open(p, 'rb').read()
    print('%9d  sha256=%s  %s' % (len(b), hashlib.sha256(b).hexdigest()[:16], p))
