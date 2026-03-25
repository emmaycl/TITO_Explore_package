from __future__ import annotations
from TITO_Explore.types import TranslationInvariantTotalOrder
from TITO_Explore.normalization import process_tito_blocks

tito1 = TranslationInvariantTotalOrder(n=3, num_blocks=2, vectors=[[0, 4], [2]], waxing_waning=[0, 0])
tito2 = TranslationInvariantTotalOrder(n=3, num_blocks=2, vectors=[[4, 3], [5]], waxing_waning=[0, 0])
tito3 = TranslationInvariantTotalOrder(n=3, num_blocks=2, vectors=[[5, 1], [9]], waxing_waning=[1, 1]) 
tito4 = TranslationInvariantTotalOrder(n=3, num_blocks=2, vectors=[[1, 2], [12]], waxing_waning=[1, 1])
tito5 = TranslationInvariantTotalOrder(n=3, num_blocks=2, vectors=[[0, 4], [2]], waxing_waning=[1, 1])
tito6 = TranslationInvariantTotalOrder(n=3, num_blocks=2, vectors=[[4, 5, 6]], waxing_waning=[0, 0])
# Normalize the TITOs
print(tito1)
normalized_tito1 = process_tito_blocks(tito1)
print(normalized_tito1)

print(tito2)
normalized_tito2 = process_tito_blocks(tito2)
print(normalized_tito2)

print(tito3)
normalized_tito3 = process_tito_blocks(tito3)
print(normalized_tito3)

print(tito4)
normalized_tito4 = process_tito_blocks(tito4)
print(normalized_tito4)

print(tito5)
normalized_tito5 = process_tito_blocks(tito5)
print(normalized_tito5)

print(tito6)
normalized_tito6 = process_tito_blocks(tito6)
print(normalized_tito6)