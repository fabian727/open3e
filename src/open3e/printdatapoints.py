"""
   Copyright 2023 philippoo66
   
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


import argparse

def readfile(file):
    dic = {}
    with open(file, 'r') as file:
        lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line:
            parts = line.split(':')
            parts[0] = parts[0].strip()
            if parts[0].isdigit():  # no def, comment etc
                if len(parts) > 1:
                    did = parts[0]
                    stuff = parts[1].strip()
                    dic[did] = stuff
    return dic


# ++++++++++++++++++
# Main
# ++++++++++++++++++
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-dev", "--dev", type=str, help="--dev vdens or vcal or vx3 or vair")
    args = parser.parse_args()

    dev = "vcal"
    devfile = ""
    unifile = "Open3Edatapoints.py"

    if(args.dev != None):
        dev = args.dev

    if('.py' in dev):
        devfile = dev
    else:
        devfile = "Open3Edatapoints" + dev.capitalize() + ".py"


    dicuni = readfile(unifile)
    dicdev = readfile(devfile)

    for did in dicdev:
        if dicdev[did].lower().startswith("none"):
            if did in dicuni:
                dicdev[did] = dicuni[did]
        print(f"{did} : {dicdev[did]}")

if __name__ == "__main__":
    main()