# Distribuição, open source e website — Southern Mercenaries

> Versão 3 · 2026-10-30 · Como o jogo é empacotado, publicado e baixado.
> Pontos marcados como **proposta** ou **em aberto** devem ser confirmados com o autor.

## 1. Objetivo

- Nome do jogo: **Southern Mercenaries**. Identificador técnico (repositório, arquivos, pasta de saves): `southern-mercenaries`.
- Jogo **open source sob GPL-3.0**, com repositório público no **GitHub** (`github.com/<usuario>/southern-mercenaries`).
- Roda em **Windows** e **Linux** (mesmo projeto Godot).
- Download pelo **website do jogo**, com um instalador por sistema.
- Tudo grátis: GitHub, GitHub Actions, GitHub Releases e GitHub Pages.

## 2. Licenças

| O quê | Licença | Observação |
|---|---|---|
| Código (GDScript, cenas, dados) | **GPL-3.0** (decidido) | Qualquer um pode usar, estudar e modificar; quem distribuir uma versão modificada precisa publicar o código sob GPL-3.0 também |
| Arte, modelos, música, sons, textos da história | **CC BY-SA 4.0** (proposta) | Arte própria do projeto; compatível em espírito com a GPL (quem modificar compartilha igual) |
| Assets de terceiros | A licença original de cada um | Só CC0, CC BY ou CC BY-SA. Registrar autor, link e licença em `CREDITS.md` |
| Godot Engine | MIT | Compatível com GPL-3.0. Incluir o aviso de licença do Godot no jogo (tela de créditos) |

- **Proibido no repositório:** assets cuja licença não permite redistribuição (ex.: Synty, a maioria dos packs pagos da Asset Store, Mixamo).
- **Plugins/bibliotecas de terceiros** precisam ser compatíveis com GPL-3.0 (MIT, BSD, Apache-2.0, LGPL, GPL).
- Arquivos `LICENSE` (texto da GPL-3.0) e `LICENSE-ASSETS` (arte) na raiz.
- Cabeçalho curto em cada script (proposta): `# Southern Mercenaries — GPL-3.0-or-later` (ou `GPL-3.0-only` — **em aberto**).
- Colaboradores: ao enviar PR, concordam que a contribuição fica sob a mesma licença (explicado em `CONTRIBUTING.md`).

## 3. Estrutura do repositório (proposta)

```
/                    projeto Godot (project.godot, nome "Southern Mercenaries")
/game/               cenas e scripts do jogo
/data/               JSON/Resources (classes, itens, monstros, missões)
/locale/             traduções (en, es, pt_BR)
/assets/             modelos, texturas, áudio
/docs/               esta documentação (.md)
/website/            site estático (GitHub Pages)
/installer/          script do Inno Setup e arquivos do AppImage
/.github/workflows/  build e release automáticos
README.md  LICENSE  LICENSE-ASSETS  CREDITS.md  CONTRIBUTING.md  CHANGELOG.md
```

## 4. Builds e instaladores

| Sistema | Formato | Ferramenta |
|---|---|---|
| Windows 10/11 x86_64 | **Instalador `.exe`** (atalho no Menu Iniciar e na área de trabalho, desinstalador) + `.zip` portátil | Export do Godot + **Inno Setup** |
| Linux x86_64 | **AppImage** (arquivo único, roda na maioria das distros) + `.tar.gz` | Export do Godot + appimagetool |

- Nome dos arquivos: `southern-mercenaries-<versão>-windows-setup.exe`, `southern-mercenaries-<versão>-windows.zip`, `southern-mercenaries-<versão>-linux-x86_64.AppImage`, `southern-mercenaries-<versão>-linux-x86_64.tar.gz`.
- O instalador do Windows mostra a licença GPL-3.0 na instalação; os pacotes incluem `LICENSE`, `LICENSE-ASSETS` e `CREDITS.md`.
- **Saves e configurações** em `user://` do Godot (Windows: `%APPDATA%\Southern Mercenaries`, Linux: `~/.local/share/southern-mercenaries`) — desinstalar não apaga os personagens.
- **Assinatura no Windows:** sem certificado, o SmartScreen mostra "editor desconhecido". v1.0 sai sem assinatura; o site explica como clicar em "Mais informações → Executar assim mesmo". Proposta futura: SignPath (grátis para open source).
- **Flatpak/Flathub** para Linux: opcional, depois da v1.0.

## 5. Build automática (GitHub Actions)

- A cada **tag de versão** (`v0.1.0`, `v1.0.0`…), o workflow:
  1. baixa o Godot (versão fixada) e os export templates;
  2. exporta Windows e Linux;
  3. gera o instalador do Windows (Inno Setup) e o AppImage;
  4. cria o **GitHub Release** com os arquivos e o changelog.
- A cada push/PR: exporta uma build de teste para verificar se o projeto abre e compila (proposta: rodar testes GDScript com GUT ou GdUnit4).
- Versionamento **SemVer**: `0.x` durante o desenvolvimento, `1.0.0` na campanha completa.

## 6. Website

- **Site estático** na pasta `/website`, publicado pelo **GitHub Pages** (proposta de domínio próprio depois), nos 3 idiomas (proposta).
- Páginas:
  - **Início:** logo "Southern Mercenaries", trailer/GIF, screenshots, descrição curta, botões **Baixar para Windows** / **Baixar para Linux** (o site detecta o sistema e destaca o botão certo).
  - **Download:** links para a última versão no GitHub Releases, requisitos mínimos, aviso do SmartScreen.
  - **Como jogar em LAN:** hospedar, entrar, liberar o firewall.
  - **Classes e mundo:** resumo das 5 classes e da história.
  - **Contribuir:** link para o repositório, `CONTRIBUTING.md`, como reportar bugs (Issues), licença GPL-3.0.
- Os botões apontam para `https://github.com/<usuario>/southern-mercenaries/releases/latest/download/<arquivo>`, que sempre baixa a versão mais recente sem editar o site (para isso, os arquivos do "latest" também são publicados sem número de versão, ex.: `southern-mercenaries-windows-setup.exe`).
- Tecnologia: HTML + CSS simples (proposta) ou Astro, sem servidor.

## 7. Atualizações

- No menu principal, o jogo consulta a API de releases do GitHub e avisa: "Nova versão disponível" com link para o site. Sem atualização automática na v1.0.
- Lembrete: no co-op, todos precisam da **mesma versão** (`01-escopo.md`, seção 4).

## 8. Rede e firewall

- Porta padrão do jogo: **UDP 24567** (jogo) e **UDP 24568** (descoberta na LAN, `07-rede.md`) — proposta.
- Windows: o instalador cria a regra de firewall para o jogo (com permissão do usuário) ou o Windows pergunta na primeira vez que hospedar.
- Linux: o site explica como liberar a porta (ufw/firewalld), se necessário.

## 9. Opcional: itch.io

- Publicar também no **itch.io** (grátis, aceita doações) com o `butler` no mesmo workflow; o app do itch instala e atualiza o jogo sozinho.

## 10. Decisões em aberto

- GPL-3.0-only ou GPL-3.0-or-later (permite versões futuras da GPL)?
- Licença da arte: CC BY-SA 4.0?
- Nome "Southern Mercenaries" igual nos 3 idiomas?
- Domínio próprio para o site?
- Aceitar doações (GitHub Sponsors, itch.io)?
- Publicar no itch.io também?
- Repositório público desde o início ou só a partir da v0.1?
