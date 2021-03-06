#!/usr/bin/env python3
import utils

from year_2018.day_03.part_a import Claims


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        '701'
        """
        non_overlapping_claims = ClaimsExtended.from_lines(_input)\
            .get_non_overlapping_claims()
        if not non_overlapping_claims:
            raise Exception("No claims are overlap-free")
        if len(non_overlapping_claims) > 1:
            raise Exception(
                f"Found {len(non_overlapping_claims)} overlap-free claims")
        non_overlapping_claim, = non_overlapping_claims

        return non_overlapping_claim.id


class ClaimsExtended(Claims):
    def get_non_overlapping_claims(self):
        """
        >>> sorted(_claim.id for _claim in ClaimsExtended.from_lines(
        ...     "#1 @ 1,3: 4x4\\n"
        ...     "#2 @ 3,1: 4x4\\n"
        ...     "#3 @ 5,5: 2x2\\n"
        ... ).get_non_overlapping_claims())
        ['3']
        >>> sorted(_claim.id for _claim in ClaimsExtended.from_lines(
        ...     "#0 @ 3,3: 2x2\\n"
        ...     "#1 @ 1,3: 4x4\\n"
        ...     "#2 @ 3,1: 4x4\\n"
        ...     "#3 @ 5,5: 2x2\\n"
        ... ).get_non_overlapping_claims())
        ['3']
        """
        seen = {}
        non_overlapping_claims = set()
        for claim in self.claims:
            claim_overlaps = False
            for square in claim.squares():
                if square not in seen:
                    seen[square] = claim
                else:
                    claim_overlaps = True
                    other_claim = seen[square]
                    if other_claim:
                        if other_claim in non_overlapping_claims:
                            non_overlapping_claims.remove(other_claim)
                        seen[square] = None
            if not claim_overlaps:
                non_overlapping_claims.add(claim)

        return non_overlapping_claims


Challenge.main()
challenge = Challenge()
