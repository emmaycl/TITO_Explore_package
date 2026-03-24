from __future__ import annotations
from TITO_Explore.types import TranslationInvariantTotalOrder
from TITO_Explore.normalization import process_tito_blocks

tito1 = TranslationInvariantTotalOrder(n=3, num_blocks=2, vectors=[[0, 4], [2]], waxing_waning=[0, 0])
tito2 = TranslationInvariantTotalOrder(n=3, num_blocks=2, vectors=[[4, 3], [5]], waxing_waning=[0, 0])
tito3 = TranslationInvariantTotalOrder(n=3, num_blocks=2, vectors=[[5, 1], [8]], waxing_waning=[1, 1]) 
tito4 = TranslationInvariantTotalOrder(n=3, num_blocks=2, vectors=[[1, 2], [11]], waxing_waning=[1, 1])
tito5 = TranslationInvariantTotalOrder(n=3, num_blocks=2, vectors=[[0, 4], [2]], waxing_waning=[1, 1])
tito6 = TranslationInvariantTotalOrder(n=3, num_blocks=2, vectors=[[4, 5, 6]], waxing_waning=[0, 0])
# Normalize the TITOs
normalized_tito1 = print(process_tito_blocks(tito1))
normalized_tito2 = print(process_tito_blocks(tito2))
normalized_tito3 = print(process_tito_blocks(tito3))
normalized_tito4 = print(process_tito_blocks(tito4))
normalized_tito5 = print(process_tito_blocks(tito5))
normalized_tito6 = print(process_tito_blocks(tito6))