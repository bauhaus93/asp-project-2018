#!/bin/python3

import random
import subprocess
import tempfile
import os

def create_random_measurements(depos, predicates, min_count, max_count, filename):
    count = random.randint(min_count, max_count)

    measurements = set()
    while len(measurements) < count:
        p = random.choice(predicates)
        d = random.choice(depos)
        v = random.randint(0, 1)
        mask = (p, d, v)
        measurements.add(mask)

    with open(filename, "w") as f:
        for mask in measurements:
            measurement = "{}({}, {}).".format(*mask)
            f.write(measurement + "\n")
    return measurements

def print_measurement(measurement):
    print("Measurement:")
    for m in measurement:
        print("{}({}, {}).".format(*m))

def find_m1_wary(lines):
    states_a = ["wary(m1)", "wary(c1)", "ok(m2)", "ok(w1)", "ok(w2)"]
    states_b = ["wary(m1)", "ok(c1)", "ok(m2)", "ok(w1)", "ok(w2)"]
    found = (False, False)
    diags = 0
    for line in lines:
        if diags > 2:
            break
        if "Diagnosis:" in line:
            diags += 1
            if found[0] == False and all(list(map(lambda state: state in line, states_a))):
                found = (True, found[1])
            elif found[1] == False and all(list(map(lambda state: state in line, states_b))):
                found = (found[0], True)
    return all(found) and diags == 2

def find_empty(lines):
    return all(list(map(lambda line: not "Diagnosis:" in line, lines)))

ALL_DEPOS = ["w1", "w2", "m1", "m2", "c1"]
ALL_PREDICATES = ["t", "s1", "s2"]
FILENAME = os.path.join(tempfile.gettempdir(), "test.obs")
CBD_CMD = ["dlv", "-silent", "-N=2", "-FRmin", "network.dl", "cbd.hyp", "cbd_cstr.dl", "cbd_fault.obs", FILENAME]
ABD_CMD = ["dlv", "-silent", "-N=2", "-FD", "abd_network.dl", "abd.hyp", "abd_cstr.dl", "abd_fault.dl", FILENAME]

DEPOS = ALL_DEPOS
PREDICATES = ["t"]

print("Using depos:", ", ".join(DEPOS))
print("Using predicates:", ", ".join(PREDICATES))

tries = 0
while True:
    measurement = create_random_measurements(DEPOS, PREDICATES, 2, 10, FILENAME)
    output = subprocess.check_output(ABD_CMD, encoding = "ISO 8859-1")
    lines = output.split("\n")
    if find_m1_wary(lines):
        print_measurement(measurement)
        break

    if tries % 1000 == 0:
        print("Tries:", tries)
    tries += 1
