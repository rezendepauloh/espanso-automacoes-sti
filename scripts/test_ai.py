# -*- coding: utf-8 -*-
from lib.utils import fix_text_with_ai
from lib.dictionary import DICIONARIO

test_text = "ola, tudo bem? aqui e o paulo do mpms. vc pode ver o problema no pc com windows? tbm preciso do pdf do sajmp"
result = fix_text_with_ai(test_text, DICIONARIO)

print(f"Original: {test_text}")
print(f"Result:   {result}")

# Teste específico do 'e' vs 'é'
test_context = "o computador e bom e o monitor e grande"
result_context = fix_text_with_ai(test_context, DICIONARIO)
print(f"\nOriginal Contexto: {test_context}")
print(f"Result Contexto:   {result_context}")
