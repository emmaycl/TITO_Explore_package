from TITO_Explore.inversion_set import (
    print_inversion_matrix,
    tito_to_inversion_set,
)
from TITO_Explore.join import compute_join_reflection_table, compute_tito_join
from TITO_Explore.types import TranslationInvariantTotalOrder


def main() -> None:
    tito1 = TranslationInvariantTotalOrder(
        n=2,
        num_blocks=1,
        vectors=[[0, 1]],
        waxing_waning=[0],
    )
    tito2 = TranslationInvariantTotalOrder(
        n=2,
        num_blocks=1,
        vectors=[[1, 2]],
        waxing_waning=[0],
    )

    print("Step 1: Inversion matrices")
    inv1 = tito_to_inversion_set(tito1)
    inv2 = tito_to_inversion_set(tito2)
    print("\nTITO1 inversion matrix:")
    print_inversion_matrix(inv1)
    print("\nTITO2 inversion matrix:")
    print_inversion_matrix(inv2)

    table_rows = compute_join_reflection_table(tito1, tito2)
    print("\nStep 2: Reflection table rows (join output):")
    print(f"{'Node':<10} | {'Value':<10} | {'Indicator':<10}")
    print("-" * 36)
    for start, value, indicator in table_rows:
        print(f"{start:<10} | {value:<10} | {indicator:<10}")

    blocks, waxing_waning, report = compute_tito_join(tito1, tito2)
    joined_tito = TranslationInvariantTotalOrder(
        n=tito1.n,
        num_blocks=len(blocks),
        vectors=blocks,
        waxing_waning=waxing_waning,
    )
    print("\nStep 3: Reconstructed join TITO")
    print("  Blocks:", blocks)
    print("  Waxing/Waning:", waxing_waning)
    print("  Report:", report)
    print("  Reconstructed TITO:", joined_tito)


if __name__ == "__main__":
    main()
