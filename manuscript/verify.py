import argparse
from collections import Counter
import hashlib
import json
from math import comb
from pathlib import Path


def compositions(total):
    if total == 0:
        yield ()
    else:
        for first in range(1, total + 1):
            for tail in compositions(total - first):
                yield (first,) + tail


def partitions(total):
    blocks = []

    def extend(vertex):
        if vertex == total:
            yield tuple(tuple(block) for block in blocks)
            return
        for block in blocks:
            block.append(vertex)
            yield from extend(vertex + 1)
            block.pop()
        blocks.append([vertex])
        yield from extend(vertex + 1)
        blocks.pop()

    yield from extend(0)


def composition_of_partition(partition, total):
    arcs = [(left, right) for block in partition for left, right in zip(block, block[1:])]
    if any(left < other_left < right < other_right
           for left, right in arcs for other_left, other_right in arcs):
        return None
    levels = Counter()
    ranks = Counter()
    for vertex in range(total):
        active = sorted(left for left, right in arcs if left < vertex <= right)
        levels[len(active)] += 1
        incoming = [left for left, right in arcs if right == vertex]
        if incoming:
            ranks[active.index(incoming[0]) + 1] += 1
    peak = max(levels)
    result = [levels[0]]
    for height in range(1, peak + 1):
        result.extend([ranks[height], levels[height] - ranks[height]])
    if result[-1] == 0:
        result.pop()
    assert all(part > 0 for part in result)
    return tuple(result)


def product_formula(composition):
    result = 1
    for left, right in zip(composition, composition[1:]):
        result *= comb(left + right - 1, right)
    return result


def partition_statistics(partition, total):
    arcs = [(left, right) for block in partition for left, right in zip(block, block[1:])]
    levels = Counter()
    ranks = Counter()
    for vertex in range(total):
        endpoints = sorted(left for left, right in arcs if left < vertex <= right)
        levels[len(endpoints)] += 1
        predecessor = next((left for left, right in arcs if right == vertex), None)
        if predecessor is not None:
            ranks[endpoints.index(predecessor) + 1] += 1
    peak = max(levels)
    return (tuple(levels[height] for height in range(peak + 1)),
            tuple(ranks[height] for height in range(1, peak + 1)))


def canonical_lift(composition):
    def contour(profile):
        if not profile:
            return ()
        return (1,) + contour(profile[1:]) + (-1,) + (1, -1) * (profile[0] - 1)

    path = contour(composition)
    stack = []
    blocks = []
    for vertex in range(sum(composition)):
        pair = path[2 * vertex:2 * vertex + 2]
        if pair == (1, 1):
            block = [vertex]
            blocks.append(block)
            stack.append(block)
        elif pair == (-1, -1):
            stack.pop().append(vertex)
        elif pair == (-1, 1):
            stack[-1].append(vertex)
        else:
            assert pair == (1, -1)
            blocks.append([vertex])
    assert not stack
    return tuple(tuple(block) for block in blocks)


def split(composition, corrected=True):
    size = len(composition)
    if size <= 2:
        return composition, composition
    if size == 3:
        return ((composition[0], composition[1] + composition[2]),
                (composition[0] + composition[2], composition[1]))
    hike = size // 2
    first = (composition[0],) + tuple(
        composition[2 * index - 1] + composition[2 * index]
        for index in range(1, hike))
    first += (composition[2 * hike - 1] +
              (composition[2 * hike] if size % 2 else 0),)
    leading = 1 - hike + sum(composition[2 * index] for index in range(hike))
    if corrected and size % 2:
        leading += composition[-1]
    second = (leading,) + tuple(1 + composition[2 * index - 1]
                                 for index in range(1, hike))
    second += (composition[2 * hike - 1],)
    return first, second


def fibonacci(rows):
    if len(rows) == 1:
        return (1,) * rows[0]
    word = (1,) * (rows[0] - 1)
    for index, row in enumerate(rows[1:], 1):
        word += (2,) + (1,) * (row - (1 if index == len(rows) - 1 else 2))
    return word


def rows_of(word):
    if 2 not in word:
        return (len(word),)
    runs = [0]
    for letter in word:
        if letter == 1:
            runs[-1] += 1
        else:
            runs.append(0)
    return tuple(run + (1 if index in (0, len(runs) - 1) else 2)
                 for index, run in enumerate(runs))


def words(total):
    if total == 0:
        yield ()
    for letter in (1, 2):
        if total >= letter:
            for tail in words(total - letter):
                yield (letter,) + tail


def dominates(first, second):
    first_sum = second_sum = 0
    for first_letter, second_letter in zip(first, second):
        first_sum += first_letter
        second_sum += second_letter
        if first_sum < second_sum:
            return False
    return True


def support_condition(first, second):
    if first.count(2) != second.count(2):
        return False
    return all(left >= right for left, right in zip(rows_of(first)[1:], rows_of(second)[1:]))


def reconstruct(first, second):
    first_rows, second_rows = rows_of(first), rows_of(second)
    hike = first.count(2)
    if hike == 0:
        return (len(first),)
    result = [first_rows[0]]
    for index in range(1, hike):
        result.extend([second_rows[index] - 1,
                       first_rows[index] - second_rows[index] + 1])
    result.append(second_rows[-1])
    if first_rows[-1] > second_rows[-1]:
        result.append(first_rows[-1] - second_rows[-1])
    return tuple(result)


def dyck_profiles(total):
    result = Counter()
    profile = [0] * total

    def extend(opened, closed):
        if closed == total:
            highest = max(index + 1 for index, count in enumerate(profile) if count)
            result[tuple(profile[:highest])] += 1
            return
        height = opened - closed
        if opened < total:
            profile[height] += 1
            extend(opened + 1, closed)
            profile[height] -= 1
        if closed < opened:
            extend(opened, closed + 1)

    extend(0, 0)
    return result


def run(partition_max=9, support_max=12, composition_max=16):
    partition_counts = []
    examined_partitions = 0
    for total in range(1, partition_max + 1):
        counts = Counter()
        observed_moments = Counter()
        for partition in partitions(total):
            examined_partitions += 1
            composition = composition_of_partition(partition, total)
            if composition is not None:
                counts[composition] += 1
                levels, ranks = partition_statistics(partition, total)
                assert levels == split(composition)[0]
                assert ranks == composition[1::2]
                observed_moments[levels, ranks] += 1
        expected = {composition: product_formula(composition)
                    for composition in compositions(total)}
        assert counts == expected
        assert counts == dyck_profiles(total)
        expected_moments = Counter()
        for composition, multiplicity in expected.items():
            expected_moments[split(composition)[0], composition[1::2]] += multiplicity
        assert observed_moments == expected_moments
        assert len({levels for levels, ranks in observed_moments}) == len(list(words(total)))
        assert len({ranks for levels, ranks in observed_moments}) == len(list(words(total)))
        catalan = comb(2 * total, total) // (total + 1)
        assert sum(counts.values()) == catalan
        partition_counts.append({'n': total, 'noncrossing_partitions': catalan,
                                 'positive_compositions': len(counts)})
    pair_count = 0
    support_rows = []
    for total in range(1, support_max + 1):
        matrix = {}
        literal = {}
        for composition in compositions(total):
            first_rows, second_rows = split(composition)
            first, second = fibonacci(first_rows), fibonacci(second_rows)
            assert sum(first) == sum(second) == total
            assert (first, second) not in matrix
            matrix[first, second] = product_formula(composition)
            literal_rows = split(composition, corrected=False)
            literal_words = tuple(fibonacci(rows) for rows in literal_rows)
            if sum(literal_words[1]) == total:
                assert literal_words not in literal
                literal[literal_words] = product_formula(composition)
        all_words = list(words(total))
        for word in all_words:
            assert matrix[word, word] == literal[word, word] > 0
            diagonal_composition = reconstruct(word, word)
            assert len(diagonal_composition) == 1 or len(diagonal_composition) % 2 == 0
        for first in all_words:
            for second in all_words:
                pair_count += 1
                supported = (first, second) in matrix
                assert supported == support_condition(first, second)
                literal_condition = support_condition(first, second) and (
                    first.count(2) < 2 or rows_of(first)[-1] == rows_of(second)[-1])
                assert ((first, second) in literal) == literal_condition
                if supported:
                    composition = reconstruct(first, second)
                    assert tuple(fibonacci(rows) for rows in split(composition)) == (first, second)
                    assert product_formula(composition) == matrix[first, second]
                    assert dominates(first, second) and first >= second
                    assert first.count(2) == second.count(2)
        for first, second in literal:
            assert dominates(first, second) and first >= second
            assert first.count(2) == second.count(2)
        hike_counts = Counter(first.count(2) for first, second in matrix)
        assert hike_counts[0] == 1
        for hike in range(1, total // 2 + 1):
            assert hike_counts[hike] == comb(total, 2 * hike)
        literal_count = 1 if total == 1 else 2 ** (total - 2) + 1 + (
            comb(total - 1, 2) if total >= 3 else 0)
        assert len(literal) == literal_count
        support_rows.append({'n': total, 'corrected_nonzero_entries': len(matrix),
                             'literal_fixed_weight_nonzero_entries': len(literal),
                             'corrected_by_hike': dict(sorted(hike_counts.items()))})
        if total == 5:
            ordered = [(2, 2, 1), (2, 1, 2), (2, 1, 1, 1), (1, 2, 2),
                       (1, 2, 1, 1), (1, 1, 2, 1), (1, 1, 1, 2), (1, 1, 1, 1, 1)]
            expected_figure = [[1, 0, 0, 1, 0, 0, 0, 0],
                               [0, 2, 0, 2, 0, 0, 0, 0],
                               [0, 0, 1, 0, 3, 3, 1, 0],
                               [0, 0, 0, 2, 0, 0, 0, 0],
                               [0, 0, 0, 0, 4, 6, 2, 0],
                               [0, 0, 0, 0, 0, 6, 3, 0],
                               [0, 0, 0, 0, 0, 0, 4, 0],
                               [0, 0, 0, 0, 0, 0, 0, 1]]
            actual_figure = [[matrix.get((first, second), 0) for second in ordered]
                             for first in ordered]
            assert actual_figure == expected_figure
    composition_count = 0
    for total in range(1, composition_max + 1):
        multiplicity_sum = 0
        for composition in compositions(total):
            composition_count += 1
            multiplicity_sum += product_formula(composition)
            first_rows, second_rows = split(composition)
            assert sum(first_rows) == sum(second_rows) == total
            assert all(left >= right for left, right in zip(first_rows[1:], second_rows[1:]))
            first, second = fibonacci(first_rows), fibonacci(second_rows)
            assert dominates(first, second)
            assert reconstruct(first, second) == composition
            lifted_partition = canonical_lift(composition)
            assert composition_of_partition(lifted_partition, total) == composition
            literal_first, literal_second = split(composition, corrected=False)
            loss = composition[-1] if len(composition) >= 5 and len(composition) % 2 else 0
            assert sum(literal_first) - sum(literal_second) == loss
        assert multiplicity_sum == comb(2 * total, total) // (total + 1)
    counterexample_first, counterexample_second = (2, 2, 1), (2, 1, 2)
    assert dominates(counterexample_first, counterexample_second)
    assert counterexample_first.count(2) == counterexample_second.count(2) == 2
    assert not support_condition(counterexample_first, counterexample_second)
    return {'status': 'pass', 'arithmetic': 'exact integers',
            'partition_definition': 'consecutive-block arcs, active predecessor ranks, Definition 8.16',
            'partition_max_n': partition_max, 'set_partitions_examined': examined_partitions,
            'dyck_profile_max_n': partition_max, 'partition_counts': partition_counts,
            'support_max_n': support_max, 'ordered_word_pairs_examined': pair_count,
            'support_counts': support_rows, 'composition_max_n': composition_max,
            'compositions_examined': composition_count, 'figure_8_n5': 'all 64 entries agree',
            'claims': ['multiplicity product formula', 'exact corrected support criterion',
                       'inverse composition reconstruction', 'prefix dominance and equal hike',
                       'descending-lex upper triangularity', 'Catalan sum',
                       'literal odd-length weight deficit', 'exact literal support criterion',
                       'statistics and moment polynomial coefficients',
                       'two one-alphabet specialization counts', 'canonical lift',
                       'positive diagonal entries', 'hike-block support counts',
                       'literal support count', 'non-asserted converse counterexample'],
            'canonical_lifts_checked': composition_count,
            'moment_polynomial_max_n': partition_max,
            'converse_example': {'u': '221', 'v': '212', 'equal_hike': 2,
                                'dominance': True, 'entry': 0,
                                'source_status': 'not asserted in the source'},
            'scope': 'finite checks complement the all-n written proofs in note.tex',
            'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    arguments = parser.parse_args()
    rendered = json.dumps(run(), indent=2, sort_keys=True) + '\n'
    if arguments.output:
        arguments.output.write_text(rendered)
    else:
        print(rendered, end='')
