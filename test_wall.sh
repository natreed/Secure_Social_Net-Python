#!/usr/bin/env bash
#{echo "/sw";
#echo "/p post from script";
#echo "/sw";
#echo "/q";
#echo "/q" ; } | python3 SSN.py

python3 SSN.py <<EOF
/sw
/p post from script
/sw
/q
/q
EOF
