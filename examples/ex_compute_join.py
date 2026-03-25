from TITO_Explore.join import compute_join_reflection_table, compute_tito_join
from TITO_Explore.types import TranslationInvariantTotalOrder


def main() -> None:
    tito1 = TranslationInvariantTotalOrder(
        n=2,
        num_blocks=1,
        vectors=[[1, 0]],
        waxing_waning=[0],
    )
    tito2 = TranslationInvariantTotalOrder(
        n=2,
        num_blocks=1,
        vectors=[[2, 1]],
        waxing_waning=[0],
    )

    blocks, waxing_waning, _ = compute_tito_join(tito1, tito2)
    print("Join window notation:")
    print("  Blocks:", blocks)
    print("  Waxing/Waning:", waxing_waning)
    
    joined_tito = TranslationInvariantTotalOrder(
        n=tito1.n,
        num_blocks=len(blocks),
        vectors=blocks,
        waxing_waning=waxing_waning,
    )
    print("  Reconstructed TITO:", joined_tito)

    table_rows = compute_join_reflection_table(tito1, tito2)

    print("\nReflection table rows:")
    print(f"{'Node':<10} | {'Value':<10} | {'Indicator':<10}")
    print("-" * 36)
    for start, value, indicator in table_rows:
        print(f"{start:<10} | {value:<10} | {indicator:<10}")


if __name__ == "__main__":
    main()
