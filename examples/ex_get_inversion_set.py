from TITO_Explore.inversion_set import (
    tito_to_inversion_set,
    print_inversion_matrix,
    print_inversion_set,
)
from TITO_Explore.types import TranslationInvariantTotalOrder


def main() -> None:
    tito = TranslationInvariantTotalOrder(
        n=4,
        num_blocks=2,
        vectors=[[0, 5, 6], [3]],
        waxing_waning=[0, 1],
    )

    print("TITO:", tito)

    inversion_matrix = tito_to_inversion_set(tito)

    print("\nInversion matrix:")
    print_inversion_matrix(inversion_matrix)

    print("\nInversion set:")
    print_inversion_set(inversion_matrix)


if __name__ == "__main__":
    main()
