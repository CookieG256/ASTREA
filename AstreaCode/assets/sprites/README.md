# Sprites personalizados

Coloque imagens PNG com transparência nesta pasta. Os sprites são redimensionados com `pygame.transform.scale` e usam pixel art sem suavização; se um arquivo não existir, o sprite procedural atual continua sendo usado.

- `items/<nome-ou-chave>.png`: armas, amuletos e outros itens.
- `armaduras/<nome-ou-chave>.png`: capacetes, peitorais e calças.
- `inimigos/<tipo>.png`: sprite genérico por tipo de inimigo.
- `inimigos/<bioma_id>/<tipo>.png`: sprite específico de um bioma, por exemplo `inimigos/1/boss.png`.

Por padrão, o nome do arquivo é derivado do nome do item ou do tipo do inimigo, em minúsculas e sem acentos. Para um item ou inimigo usar outro nome, defina `"sprite": "chave-do-arquivo"` nos respectivos dados; não inclua a extensão `.png`.

Após adicionar ou substituir imagens, reinicie o jogo para atualizar os sprites armazenados em cache.
