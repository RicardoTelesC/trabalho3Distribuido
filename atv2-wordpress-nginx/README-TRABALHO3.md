# Trabalho 3 — Testes de carga com Locust

Extensão do ambiente do **Trabalho 2** (WordPress + Nginx + MySQL) para avaliar desempenho com o [Locust](https://locust.io/).

## O que foi adicionado

| Item | Descrição |
|------|-----------|
| Serviço `locust` | No `docker-compose.yml`, rede `backend`, host alvo `http://nginx` |
| Scripts Locust | `locust/locustfile_cenario*.py` — um arquivo por cenário |
| Nginx 1/2 WP | `nginx.1wp.conf`, `nginx.2wp.conf` (3 instâncias = `nginx.conf`) |
| Profiles Docker | `wordpress2` (`wp2`), `wordpress3` (`wp3`) para ligar 1, 2 ou 3 instâncias |
| Automação | Scripts em `scripts/` para subir instâncias, rodar testes e gerar gráficos |

## Cenários de teste (enunciado)

1. **Post com imagem ~1 MB** → `locustfile_cenario1_imagem_1mb.py`
2. **Post com texto ~400 KB** → `locustfile_cenario2_texto_400kb.py`
3. **Post com imagem ~300 KB** → `locustfile_cenario3_imagem_300kb.py`

Cada script faz `GET` em `/?p=<id>` (padrão `2`, `3` e `4`). Ajuste os IDs após criar os posts no WordPress.

### 1. Gerar arquivos de conteúdo

```powershell
cd atv2-wordpress-nginx
python scripts/gerar_conteudo_teste.py
```

Arquivos em `conteudo-teste/`:

- `imagem_1mb.jpg`
- `imagem_300kb.jpg`
- `texto_400kb.txt`

### 2. Subir o WordPress e criar os posts

```powershell
$env:NGINX_CONFIG = "./nginx.conf"
docker compose --profile wp2 --profile wp3 up -d
```

Aguarde ~60 s e acesse **http://localhost/** — conclua a instalação do WordPress.

Crie **três posts publicados**:

| Cenário | Conteúdo | Slug sugerido |
|---------|----------|---------------|
| 1 | Inserir mídia `imagem_1mb.jpg` | `post-imagem-1mb` |
| 2 | Colar conteúdo de `texto_400kb.txt` | `post-texto-400kb` |
| 3 | Inserir mídia `imagem_300kb.jpg` | `post-imagem-300kb` |

Anote os IDs na lista de posts (coluna **ID**) ou na URL `/?p=ID`.

Atualize os defaults em `locust/locustfile_cenario*.py` (`POST_PATH`) ou passe `-PostPath "/?p=5"` no script headless.

## Executar testes

### Interface web (manual)

Com a stack no ar:

```powershell
docker compose up -d locust
```

Abra **http://localhost:8089/**, defina usuários/spawn rate e inicie o teste. O host já aponta para `http://nginx`.

Troque o cenário editando o `command` do serviço `locust` no `docker-compose.yml` ou rode:

```powershell
docker compose run --rm -p 8089:8089 locust `
  -f /mnt/locust/locustfile_cenario2_texto_400kb.py `
  --host=http://nginx
```

### Headless (CSV para gráficos)

Um teste:

```powershell
.\scripts\run_locust_headless.ps1 -Cenario cenario1 -Usuarios 10 -Instancias 3
```

Matriz completa (10, 100, 1000 usuários × 1, 2, 3 instâncias × 3 cenários) — **demorado**:

```powershell
.\scripts\run_matriz_testes.ps1
```

Resultados em `resultados/`; índice em `resultados/manifest.json`.

### Gráficos (entregáveis)

```powershell
pip install matplotlib
python scripts/gerar_graficos.py
```

PNG em `graficos/`:

- Requisições/s
- Tempo médio (ms)
- Percentil 95 (ms)

Eixo X: usuários ou instâncias WordPress (conforme o enunciado).

## Variar instâncias WordPress (1, 2 ou 3)

```powershell
.\scripts\set_instancias.ps1 -Instancias 2
```

| Instâncias | Comando equivalente |
|------------|---------------------|
| 1 | `docker compose up -d` + `NGINX_CONFIG=./nginx.1wp.conf` |
| 2 | `--profile wp2` + `nginx.2wp.conf` |
| 3 | `--profile wp2 --profile wp3` + `nginx.conf` |

O script `set_instancias.ps1` faz isso automaticamente.

## Imagem Docker do Locust

O PDF cita `grubykarol/locust` com `ATTACKED_HOST` e `LOCUST_OPTS`. Este projeto usa **`locustio/locust:2.29.0`** (mesma função, API atual com `HttpUser`). Para usar a imagem do PDF:

```yaml
locust:
  image: grubykarol/locust
  environment:
    ATTACKED_HOST: http://nginx
    LOCUST_FILE: locustfile_cenario1_imagem_1mb.py
    LOCUST_OPTS: "-c 10 -r 10"
```

Adapte o `locustfile` para a API antiga (`HttpLocust` / `TaskSet`) se necessário.

## Checklist de entrega

- [ ] Três posts conforme tamanhos aproximados do enunciado
- [ ] Cada cenário testado com **≥3** níveis de usuários (ex.: 10, 100, 1000)
- [ ] Cada cenário testado com **≥3** quantidades de instâncias WP (1, 2, 3)
- [ ] Gráficos de métricas Locust (RPS, tempo de resposta, etc.)
- [ ] Relatório interpretando balanceamento e escalabilidade

## Observações

- **1000 usuários** pode sobrecarregar um PC comum; reduza `-DuracaoSegundos` ou use máquina mais forte.
- O Locust acessa `http://nginx` **dentro** da rede Docker — equivalente ao host do Trabalho 2.
- Mantenha o header `X-Upstream` no Nginx para verificar distribuição entre containers durante testes leves.
