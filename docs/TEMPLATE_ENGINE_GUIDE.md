# Template Engine Guide

## Clustering Strategy

`EnterpriseUtility.cluster_templates` groups template files by counting
their placeholder markers and applying ``KMeans``. The resulting
``cluster_output.json`` maps cluster labels to template paths for further
analysis.

## Cleanup Flow

After clustering, the utility invokes
``UnifiedLegacyCleanupSystem.remove_redundant_templates``. The cleanup
routine hashes each template's contents and removes duplicates within a
cluster, ensuring only unique templates remain on disk and in the
returned mapping.

