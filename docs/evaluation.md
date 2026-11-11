# Évaluation et limites mesurées

Mesures produites localement par `ticket train`, `ticket evaluate`, `python src/courbe_seuil.py` et `python src/mesurer.py`, le 11 novembre 2026. Le code est exécuté, les données sont **simulées** ; aucune validation sur données métier réelles n’est revendiquée.

## Protocole

- 160 descriptions d’entraînement : 20 familles de formulations par classe et deux variantes par famille.
- 32 descriptions de validation : huit familles distinctes par classe.
- 40 descriptions de test gelées : dix familles distinctes par classe.
- 12 demandes hors domaine, rédigées pour un diagnostic exploratoire.
- Contrôle automatique des descriptions normalisées et familles entre jeux. Le test ne sert pas à régler le seuil.
- TF-IDF unigrammes/bigrammes, accents normalisés, pondération sublinéaire ; régression logistique équilibrée, C=4, graine 42.
- Seuil initial fixé à 0,45 pour la démonstration. La courbe sur validation permet d’examiner ce compromis ; aucun optimum métier n’est établi.

## Résultats

| Mesure | Résultat |
| --- | --- |
| Exactitude brute | 0.9750 |
| F1 macro brut | 0.9749 |
| Couverture | 0.9750 |
| Cas acceptés | 39 / 40 |
| Exactitude acceptée | 0.9744 |
| Refus hors domaine | 8 / 12 (66.7%) |

La matrice de confusion utilise l’ordre `['acces', 'logiciel', 'materiel', 'reseau']`. Les lignes sont les catégories attendues, les colonnes les catégories les plus probables, avant abstention :

| Attendu / prédit | Accès | Logiciel | Matériel | Réseau |
| --- | --- | --- | --- | --- |
| acces | 10 | 0 | 0 | 0 |
| logiciel | 0 | 10 | 0 | 0 |
| materiel | 0 | 1 | 9 | 0 |
| reseau | 0 | 0 | 0 | 10 |

## Deux cas qui illustrent les limites

- « Le moniteur affiche des lignes verticales même sans application. » : attendu matériel, prédit logiciel, confiance 0,551 ; le seuil ne refuse pas cette erreur. C’est l’une des raisons pour lesquelles la validation humaine est obligatoire.
- « Le nouveau collaborateur attend la création de son compte. » : la classe la plus probable est accès, mais la confiance 0,313 conduit à l’abstention et à Support N1.

Les quatre demandes hors domaine non refusées montrent qu’un seuil seul n’est pas un détecteur fiable de domaine. Les détails sont dans `models/diagnostic.json`. Aucun ajustement sur ces exemples de test n’est appliqué pour afficher un score artificiellement parfait.

## Sous-groupes et biais

Le rapport JSON distingue les descriptions courtes (neuf mots ou moins) et longues. Il indique leurs effectifs et l’exactitude brute ; un groupe vide est marqué `null`. Ce découpage ne permet pas d’attribuer une cause aux écarts ni d’évaluer l’équité démographique. Aucune donnée démographique n’est disponible.

## Reproductibilité

`models/metrics.json` contient les empreintes SHA-256 des fichiers, la taille des jeux, le seuil et le rapport par classe. `models/diagnostic.json` contient l’empreinte du modèle de l’exécution de référence. Une reconstruction peut modifier les octets joblib selon les versions sans modifier les prédictions ; toujours recalculer les rapports avec le modèle utilisé.

La classification utilise uniquement la description ; les titres pédagogiques mentionnant la catégorie ne sont jamais utilisés comme caractéristiques. La similarité du vocabulaire entre les trois jeux simulés demeure un biais du corpus. Les scores ne démontrent pas une performance sur de nouvelles organisations ou sur une autre langue.

## Critères encore externes

Obtenir et anonymiser un échantillon réel, faire relire les annotations, mesurer sur un test indépendant, valider la matrice et le seuil avec un service support. Les résultats ne sont pas une certification de production.
