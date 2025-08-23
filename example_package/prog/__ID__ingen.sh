#!/bin/bash

# This script first stresstests the model solution for 10 seconds
# and if it passes, it will generate the proper tests.
# To generate both types of tests, it executes ingen.cpp and passes it some arguments.
# The `test_ids` variable needs to have a manually written list of all proper tests.

prog_dir="$(realpath "$(dirname "$0")")"
cache_dir="$prog_dir/../.cache"
mkdir -p "$cache_dir"
script_name="$(basename "$0")"
task_id=${script_name%ingen.sh}
gen_exe="$cache_dir/${task_id}ingen"
sol_exe="$cache_dir/${task_id}solution"
slo_exe="$cache_dir/${task_id}slow"
stresstest_seconds=10
function compile_cpp {
	g++ -std=c++23 -O3 -lm -Werror -Wall -Wextra -Wshadow -Wconversion -Wno-unused-result -Wfloat-equal "$1" -o "$2" \
		|| exit 1
}

# Change the list of tests to generate and (if needed) the paths of solutions.
test_ids="0a 1a 2a"
compile_cpp "$prog_dir/${task_id}ingen.cpp" "$gen_exe"
compile_cpp "$prog_dir/${task_id}.cpp" "$sol_exe"
compile_cpp "$prog_dir/${task_id}s.cpp" "$slo_exe"

for (( i=0, SECONDS=0; SECONDS < stresstest_seconds; i++ )); do
	in_test="$cache_dir/input.in"
	slo_out="$cache_dir/slo.out"
	sol_out="$cache_dir/sol.out"
	printf "Running stresstest $i\r"
    "$gen_exe" stresstest $i > "$in_test"     || { echo "Failed to generate test $i";  exit 1; }
    "$slo_exe" < "$in_test" > "$slo_out"      || { echo "Brute crashed on test $i";    exit 1; }
    "$sol_exe" < "$in_test" > "$sol_out"      || { echo "Solution crashed on test $i"; exit 1; }
    diff "$slo_out" "$sol_out" -w > /dev/null || { echo "Outputs differ on test $i";   exit 1; }
done
echo "Stresstest passed with $i tests"

for test in $test_ids; do
	"$gen_exe" "$test" > "$prog_dir/../in/${task_id}${test}.in" || { echo "Failed to generate test $test"; exit 1; }
done
