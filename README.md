# Dashboard

Criei um dashboard utilizando o Streamlit, que está disponível no Streamlit Community Cloud através do link: https://teste-m2b-app.streamlit.app/

Motivação deste dashboard em Streamlit:
- Disponibilidade para acesso online pelo computador.
- Disponibilidade para acesso online pelo celular.
- Alto poder de customização (Ex: Chatbots, Integração com IA, Relatórios Automatizados etc.).
- Grande poder de interação e coleta de insights.
- Facilidade de construção.

# Descrição do Teste

Selecionar 10.000 casos com as seguintes exigências:
- Retirar casos em que o telefone é inválido;
- Retirar casos que já converteram -> Fazer um join com a base de tratativas para selecionar os casos que já converteram;
- Selecionar os casos com as melhores ofertas -> Basicamente, São os casos em que estas colunas têm os melhores valores nesta ordem: FLG_ESPECIAL > PLANO_INDICADO > DESCONTO_DESTINO > CLUSTER.

# Considerações Gerais

## Telefone

Em relação aos números, considerei que ele só será válido se, e somente se, atendes os seguintes requisitos:
- Tiver um total de 11 dígitos. Exemplo:
  - No número (21) 98282-3737, o total de dígitos de 21982823737 é 11;
- O código de área for válido. Exemplo:
  - No número (21) 98282-3737, 21 é um código válido;
- Tiver o algarismo 9 na terceira posição da esquerda pra direita. Exemplo:
  - Na terceira posição, da esquerda pra direita, do número (21) 98282-3737, há o algarismo 9.

Em relação aos números duplicados, que só estão presentes na base de teste, utilizarei a seguinte abordagem:
- Mantes na base o caso em que a idade do contato é a maior
  - Exemplo: Em dois casos com o mesmo número, um caso pode ter IDADE classificada em '31 A 45' e o outro caso pode ter IDADE classificada em 'ACIMA DE 45'. Neste caso, será mantido somente o caso em que a idade é 'ACIMA DE 45'.
- Considerando que a classificação de idade seja a mesma nos casos duplicados, manter na base o caso em que o contato pela Mobi2buy seja o mais recente.
  - Utilizar FLG_FRESCOR para esta regra;
- Em casos duplicados que haja igualdade nas variáveis IDADE e FLG_FRESCOR, manter o caso com a melhor oferta nesta ordem:
  - FLG_ESPECIAL > PLANO_INDICADO > DESCONTO_DESTINO > CLUSTER.

## Ofertas

Após uma análise dos dados, encontrei as seguintes relações entre colunas:

Considerando FLG_ESPECIAL = 1:

- Se PLANO_INDICADO = A, então:
    - BONUS_DESTINO: 14GB
    - DESCONTO_DESTINO: 15%

- Se PLANO_INDICADO = L, então:
    - BONUS_DESTINO: 10GB + 20GB
    - DESCONTO_DESTINO: 17 NFIDEL ou 20 NFIDEL

- Se PLANO_INDICADO = S, então:
    - BONUS_DESTINO: 20GB + 20GB
    - DESCONTO_DESTINO: 25 NFIDEL, 28 NFIDEL, 37 NFIDEL, 40 NFIDEL, 41 NFIDEL ou 43 NFIDEL

Considerando FLG_ESPECIAL = 0:

- Se PLANO_INDICADO = C, então:
    - BONUS_DESTINO: 20GB
    - DESCONTO_DESTINO: 00 NFIDEL

- Se PLANO_INDICADO = B, então:
    - BONUS_DESTINO: 20GB
    - DESCONTO_DESTINO: 00 NFIDEL

- Se PLANO_INDICADO = A, então:
    - BONUS_DESTINO: 9GB
    - DESCONTO_DESTINO: 5% ou 15%

- Se PLANO_INDICADO = L, então:
    - BONUS_DESTINO: 20GB
    - DESCONTO_DESTINO: 17 NFIDEL ou 20 NFIDEL

- Se PLANO_INDICADO = S, então:
    - BONUS_DESTINO: 10GB + 20GB
    - DESCONTO_DESTINO: 25 NFIDEL, 28 NFIDEL, 37 NFIDEL, 40 NFIDEL, 41 NFIDEL ou 43 NFIDEL