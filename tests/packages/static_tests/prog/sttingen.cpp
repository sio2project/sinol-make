#include <bits/stdc++.h>
#include "oi.h"
#include "config.hpp"

using namespace std;

constexpr inline std::string_view task_id = "stt";

[[nodiscard]] std::string toLetters(size_t number)
{
	constexpr size_t alpha = 'z' - 'a' + 1;

	std::string out;
	while (number > 0)
	{
		--number;
		out += static_cast<char>('a' + number % alpha);
		number = number / alpha;
	}
	std::ranges::reverse(out);
	return out;
}

std::string get_test_name(size_t group_id, size_t test_id)
{
	return (std::stringstream{} << task_id << group_id << toLetters(test_id) << ".in").str();
}

size_t next_non_static(size_t group_id, size_t test_id)
{
	while (static_test_names.contains(get_test_name(group_id, test_id)))
	{
		++test_id;
	}
	return test_id;
}

template <class T>
void printTestCases(const std::vector<std::vector<T>> &test_cases)
{
	for (size_t group_id = 0; group_id < test_cases.size(); ++group_id)
	{
		size_t test_id = next_non_static(group_id, 0);

		for (const auto &test_case : test_cases[group_id])
		{
			std::string test_name = get_test_name(group_id, test_id);
			std::cout << "Writing: " << test_name << "...\n";
			std::ofstream{test_name} << test_case;

			test_id = next_non_static(group_id, test_id + 1);
		}
	}
}

int main()
{
	printTestCases<std::string>({
		{},
		{"1 2\n", "1 4\n"},
		{"2 5\n"},
		{"3 7\n"},
		{"4 9\n"},
	});
}
