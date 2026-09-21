---
description: "Regeln für die Entwicklung und Erweiterung der Multi-Cloud Terraform/Terragrunt Infrastruktur in 02-copilot."
applyTo: "**/02-copilot/**/*.hcl, **/02-copilot/**/*.tf, **/02-copilot/**/*.md"
---

# Terraform / Terragrunt Multi-Cloud Instructions

## Ziel

Dieses Projekt ist eine Lern- und Experimentierumgebung für eine professionelle
Multi-Cloud-Infrastruktur mit Terraform und Terragrunt.

Die aktuell vorhandene AWS-Struktur dient als Referenz für die Architektur.

Die Infrastruktur soll schrittweise um Azure und Google Cloud erweitert werden.

Dabei gelten folgende Grundprinzipien:

- Bestehende Strukturen nicht unnötig verändern.
- Keine unnötigen Abstraktionen erzeugen.
- Keine Werte unnötig duplizieren.
- Wiederverwendbare Werte auf der höchstmöglichen sinnvollen Ebene definieren.
- Provider-spezifische Besonderheiten berücksichtigen.
- Terraform für die eigentliche Infrastruktur verwenden.
- Terragrunt für Environment-, Account-/Subscription-/Project-, Region- und
  Deployment-Konfiguration verwenden.
- Die Struktur soll nachvollziehbar und für Menschen wartbar bleiben.
- Änderungen sollen möglichst klein und nachvollziehbar sein.

---

# 1. Bestehende Architektur

Die aktuelle Projektstruktur ist:

    02-copilot/
    ├── terragrunt/
    │   ├── aws/
    │   │   ├── infra/
    │   │   ├── dev/
    │   │   ├── tst/
    │   │   └── pro/
    │   ├── azure/
    │   │   ├── infra/
    │   │   ├── dev/
    │   │   ├── tst/
    │   │   └── pro/
    │   ├── gcp/
    │   │   ├── infra/
    │   │   ├── dev/
    │   │   ├── tst/
    │   │   └── pro/
    │   ├── common.hcl
    │   ├── root.hcl
    │   └── versions.hcl
    │
    ├── terraform/
    │   └── modules/
    │       ├── aws/
    │       ├── azure/
    │       └── gcp/
    │
    └── README.md

Diese Struktur ist beabsichtigt und soll nicht ohne ausdrücklichen Auftrag
grundlegend verändert werden.

Insbesondere darf keine zusätzliche Ebene `live/` eingeführt werden.

---

# 2. Environment-Struktur

Für alle drei Cloud Provider soll das konzeptionelle Environment-Modell
konsistent bleiben:

- `infra`
- `dev`
- `tst`
- `pro`

Dabei bedeutet `infra` eine funktionale Shared-Service-Umgebung und ist
nicht einfach ein Synonym für "Production" oder "Live".

Beispiel AWS:

    aws/
    ├── infra/
    ├── dev/
    ├── tst/
    └── pro/

Azure und GCP sollen dasselbe übergeordnete Environment-Modell verwenden,
auch wenn die technische Umsetzung provider-spezifisch unterschiedlich ist.

---

# 3. Provider-spezifische Unterschiede respektieren

AWS, Azure und Google Cloud dürfen nicht künstlich gleich gemacht werden.

Verwende die nativen Konzepte des jeweiligen Cloud Providers.

Beispiele:

AWS:
- Account
- Region
- Availability Zones
- VPC
- Transit Gateway
- IAM

Azure:
- Subscription
- Region
- Availability Zones
- VNet
- VNet Peering / entsprechende Netzwerkdienste
- Entra ID / Managed Identity / RBAC

Google Cloud:
- Project
- Region
- Zone
- VPC Network
- Cloud DNS
- IAM

Die gemeinsame Struktur soll auf der organisatorischen Ebene bestehen.

Die Implementierung innerhalb der Provider-Module muss dagegen den jeweiligen
Cloud-Best-Practices entsprechen.

---

# 4. Minimale Wiederholung

Vermeide Konfigurationsduplikation.

Wenn ein Wert für mehrere untergeordnete Ebenen identisch ist, soll er auf
der höchstmöglichen sinnvollen gemeinsamen Ebene definiert werden.

Beispiel:

Nicht:

    dev/eu-west-1/vpc/terragrunt.hcl
        region = "eu-west-1"

    dev/eu-west-1/eks/terragrunt.hcl
        region = "eu-west-1"

    dev/eu-west-1/iam/terragrunt.hcl
        region = "eu-west-1"

Sondern:

    aws/region.hcl

mit:

    inputs = {
      region = "eu-west-1"

      azs = [
        "eu-west-1a",
        "eu-west-1b",
        "eu-west-1c"
      ]
    }

Die untergeordneten Terragrunt-Konfigurationen sollen diese Werte über
`include` und `locals` verwenden.

---

# 5. Hierarchie der Konfiguration

Bei der Entwicklung neuer Konfigurationen immer zuerst prüfen:

1. Ist der Wert global für das gesamte Projekt?
2. Ist der Wert für einen Cloud Provider gültig?
3. Ist der Wert für einen Account / eine Subscription / ein Project gültig?
4. Ist der Wert für eine Region gültig?
5. Ist der Wert für ein Environment gültig?
6. Ist der Wert nur für eine einzelne Komponente gültig?

Der Wert soll auf der niedrigsten Ebene definiert werden, auf der er sich
tatsächlich unterscheidet.

Beispiel:

    Projekt
        │
        ├── common.hcl
        │
        ├── AWS
        │   ├── account.hcl
        │   ├── region.hcl
        │   ├── infra
        │   ├── dev
        │   ├── tst
        │   └── pro
        │
        ├── Azure
        │   ├── subscription.hcl
        │   ├── region.hcl
        │   ├── infra
        │   ├── dev
        │   ├── tst
        │   └── pro
        │
        └── GCP
            ├── project.hcl
            ├── region.hcl
            ├── infra
            ├── dev
            ├── tst
            └── pro

Keine Werte auf einer niedrigeren Ebene wiederholen, wenn sie bereits
auf einer übergeordneten Ebene verfügbar sind.

---

# 6. Terragrunt-Inheritance

Verwende Terragrunt `include` und `read_terragrunt_config()` gezielt, um
übergeordnete Konfigurationen wiederzuverwenden.

Bevor neue Werte definiert werden, prüfen, ob sie bereits aus einer
übergeordneten Konfiguration übernommen werden können.

Beispiel:

    include "root" {
    path   = find_in_parent_folders("root.hcl")
      expose = true
    }

Untergeordnete Konfigurationen sollen bevorzugt Werte aus der Parent-Konfiguration
verwenden:

    include.root.locals.region.region

    include.root.locals.region.azs

Vermeide Copy & Paste zwischen `dev`, `tst` und `pro`.

---

# 7. Account / Subscription / Project

Cloud-spezifische Identitäten gehören auf die entsprechende Provider-Ebene.

AWS:

    account.hcl

Azure:

    subscription.hcl

GCP:

    project.hcl

Diese Informationen dürfen nicht in jedem einzelnen Modul oder Environment
wiederholt werden.

Beispiel AWS:

    account_id = "123456789012"

Nicht in:

    dev/vpc
    dev/eks
    dev/iam
    tst/vpc
    tst/eks
    pro/vpc
    pro/eks

jeweils erneut definieren.

---

# 8. Regionen und Availability Zones

Regionsinformationen sollen zentral auf Provider-/Regions-Ebene definiert
werden.

Beispiel AWS:

    region.hcl

    inputs = {
      region = "eu-west-1"

      azs = [
        "eu-west-1a",
        "eu-west-1b",
        "eu-west-1c"
      ]
    }

Untergeordnete Komponenten sollen diese Werte verwenden.

Nicht dieselben Regions- oder AZ-Werte mehrfach in verschiedenen
`terragrunt.hcl` Dateien definieren.

Für Azure und GCP soll dasselbe Prinzip verwendet werden, wobei die jeweiligen
Cloud-Konzepte berücksichtigt werden.

---

# 9. Terraform Module

Terraform-Module befinden sich ausschließlich unter:

    terraform/modules/

Die Module sind nach Cloud Provider getrennt:

    terraform/modules/aws/
    terraform/modules/azure/
    terraform/modules/gcp/

Beispiele:

    terraform/modules/aws/vpc
    terraform/modules/aws/eks

    terraform/modules/azure/vnet
    terraform/modules/azure/aks

    terraform/modules/gcp/network
    terraform/modules/gcp/gke

Keine künstliche Vereinheitlichung unterschiedlicher Cloud-Ressourcen erzwingen.

Eine AWS VPC muss nicht durch ein gemeinsames "network"-Modul mit Azure VNet
oder GCP VPC abstrahiert werden.

---

# 10. Terragrunt und Terraform klar trennen

Terragrunt beschreibt:

- Environment
- Account / Subscription / Project
- Region
- zentrale Konfiguration
- Backend
- Provider-Konfiguration
- Modulquelle
- Deployment-Parameter

Terraform beschreibt:

- Ressourcen
- Variablen
- Outputs
- eigentliche Infrastruktur

Keine umfangreiche Infrastruktur-Logik in Terragrunt implementieren,
wenn sie sinnvoll in ein Terraform-Modul gehört.

---

# 11. State

Jeder Cloud Provider verwendet seinen nativen bzw. passenden Backend-Mechanismus.

AWS:
- S3
- State Locking gemäß aktuellem Terraform/AWS-Best-Practice

Azure:
- Azure Storage Account / Blob Storage

GCP:
- Google Cloud Storage

State-Konfiguration soll möglichst zentral vererbt werden.

Nicht für jedes einzelne Modul eine komplett eigene Backend-Konfiguration
duplizieren.

---

# 12. Provider-Konfiguration

Provider-Konfiguration soll zentral auf der jeweiligen Cloud-Ebene erfolgen.

AWS:

- Region aus `region.hcl`
- Account-ID aus `account.hcl`
- `allowed_account_ids` verwenden, sofern sinnvoll

Azure:

- Subscription / Tenant / Region aus zentraler Konfiguration

GCP:

- Project / Region aus zentraler Konfiguration

Hardcodierte Werte in einzelnen Modulen vermeiden, wenn diese bereits
übergeordnet definiert werden können.

---

# 13. Environment-spezifische Werte

Nur Werte, die tatsächlich zwischen `dev`, `tst` und `pro` variieren,
sollen auf Environment-Ebene definiert werden.

Beispiele:

    network_cidr
    subnet CIDRs
    instance sizes
    node counts
    environment names
    production-specific settings

Nicht erneut definieren:

    region
    availability zones
    account ID
    subscription ID
    project ID

wenn diese bereits auf einer übergeordneten Ebene definiert sind.

---

# 14. Bestehende AWS-Struktur als Referenz

Die bestehende AWS-Implementierung ist die Referenz für:

- Hierarchie
- Namenskonventionen
- Inheritance
- Konfigurationsprinzipien
- Trennung zwischen Terraform und Terragrunt
- Minimierung von Wiederholungen

Beim Erstellen von Azure und GCP soll diese Struktur als Orientierung dienen.

Nicht einfach AWS-Dateien kopieren und lediglich Provider-Namen ersetzen.

Stattdessen:

1. bestehendes AWS-Konzept verstehen
2. gemeinsame Architektur erkennen
3. provider-spezifische Unterschiede identifizieren
4. Azure/GCP nach deren Best Practices implementieren
5. gemeinsame Werte auf übergeordneter Ebene halten
6. unnötige Wiederholungen vermeiden

---

# 15. Änderungen an der bestehenden Struktur

Vor jeder größeren Änderung zuerst die vorhandene Struktur analysieren.

Keine neuen Ebenen oder Dateien erzeugen, wenn eine vorhandene Ebene dafür
geeignet ist.

Insbesondere nicht automatisch hinzufügen:

- `live/`
- zusätzliche Environment-Ebenen
- zusätzliche Wrapper-Module
- unnötige Abstraktionsmodule
- doppelte Provider-Konfiguration
- doppelte Region-Konfiguration
- doppelte Account-/Subscription-/Project-Konfiguration

Wenn mehrere mögliche Architekturen existieren, die einfachste Lösung
bevorzugen, die zur bestehenden Struktur passt.

---

# 16. Copilot Arbeitsweise

Bevor Änderungen vorgenommen werden:

1. Bestehende Verzeichnisstruktur analysieren.
2. Vorhandene AWS-Konfiguration analysieren.
3. Vorhandene `terragrunt.hcl`, `account.hcl`, `region.hcl`,
   `common.hcl` und `versions.hcl` berücksichtigen.
4. Prüfen, ob benötigte Variablen bereits übergeordnet existieren.
5. Nur fehlende Konfiguration ergänzen.
6. Provider-spezifische Best Practices anwenden.
7. Keine unnötigen Dateien oder Abstraktionen erzeugen.
8. Änderungen nachvollziehbar und möglichst klein halten.

Bei Unsicherheit nicht einfach eine neue Architektur erfinden.

Zuerst die bestehende Struktur und deren Vererbungsmodell berücksichtigen.

---

# 17. Ziel

Das Ziel ist eine Multi-Cloud-Struktur, die:

- AWS, Azure und GCP unterstützt
- `infra`, `dev`, `tst` und `pro` verwendet
- Provider-spezifische Best Practices berücksichtigt
- Terraform und Terragrunt sauber trennt
- Konfiguration über Hierarchien vererbt
- minimale Wiederholung enthält
- keine unnötigen Abstraktionen besitzt
- einfach nachvollziehbar und wartbar bleibt

Grundprinzip:

**So wenig Duplikation wie möglich, so viel explizite Struktur wie nötig.**

> Learn. Build. Experiment. Understand.
