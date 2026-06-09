# Pipeline GitOps completo com ArgoCD

Um pipeline **GitOps** de ponta a ponta: você dá `git push`, o **GitHub Actions**
builda e publica a imagem, atualiza o estado desejado **no próprio Git**, e o
**ArgoCD** sincroniza automaticamente o cluster Kubernetes para bater com o Git.

> O Git é a **única fonte da verdade**. Ninguém faz `kubectl apply` na mão — o
> cluster sempre reflete o que está versionado. É assim que empresas grandes
> entregam software.

---

## 🔄 Como funciona o fluxo GitOps

```
 dev: git push (código da app)
        │
        ▼
┌──────────────────────┐
│   GitHub Actions (CI) │
│  1. build da imagem   │
│  2. push pro GHCR      │
│  3. atualiza a tag em  │
│     manifests/ e faz   │
│     commit de volta    │
└──────────┬───────────┘
           │  (novo estado desejado no Git)
           ▼
┌──────────────────────┐        ┌─────────────────────┐
│       ArgoCD          │ ─sync─▶│  Cluster Kubernetes │
│  observa o repo Git   │        │   (namespace demo)  │
│  e reconcilia o cluster│       └─────────────────────┘
└──────────────────────┘
```

**CI (push)** entrega a imagem e escreve o estado desejado.
**CD (pull)** é o ArgoCD reconciliando o cluster a partir do Git — com
`prune` e `selfHeal` ligados.

---

## 📁 Estrutura

```
gitops-argocd-pipeline/
├── app/                          # Aplicação conteinerizada
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── manifests/                    # Estado desejado (o ArgoCD observa isto)
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml        # a tag da imagem é atualizada pelo CI
├── argocd/
│   └── application.yaml          # Application do ArgoCD (auto-sync + self-heal)
└── .github/workflows/
    └── ci.yml                    # build + push + bump da imagem (GitOps)
```

---

## 🚀 Como rodar (cluster local)

### 1. Pré-requisitos
Um cluster local (kind ou minikube) e `kubectl`.

### 2. Instale o ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 3. Registre a aplicação no ArgoCD

```bash
kubectl apply -f argocd/application.yaml
```

Pronto. O ArgoCD passa a observar a pasta `manifests/` deste repositório e
sincroniza o cluster sozinho.

### 4. Acesse a UI do ArgoCD

```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
# usuário: admin
# senha:
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
```

Abra https://localhost:8080 e veja a aplicação `gitops-app` sincronizando.

---

## 🧪 Vendo o GitOps em ação

1. Altere algo em `app/app.py` e dê `git push`.
2. O **CI** builda a imagem, publica no GHCR e faz commit da nova tag em
   `manifests/kustomization.yaml`.
3. O **ArgoCD** detecta a mudança no Git e atualiza o Deployment sozinho —
   sem nenhum `kubectl apply` manual.

Teste o **self-heal**: apague um Pod ou edite o Deployment na mão
(`kubectl -n demo edit deploy/gitops-app`). O ArgoCD reverte para o estado
do Git automaticamente.

---

## 🔐 Por que isso importa

- **Git como fonte única da verdade** — todo o estado é versionado e auditável.
- **Rollback é um `git revert`** — voltar de versão é só reverter o commit.
- **Self-heal** — mudanças manuais no cluster são desfeitas automaticamente.
- **Separação CI / CD** — o CI não tem acesso direto ao cluster; quem aplica é
  o ArgoCD, puxando do Git (modelo *pull*, mais seguro).

---

## 🧰 Stack

`GitHub Actions` · `ArgoCD` · `Kubernetes` · `Kustomize` · `Docker` · `GHCR`

---

Feito por **Maria Eduarda** — foco em DevOps & Cloud (AWS).
[GitHub](https://github.com/Dudainfinity)
