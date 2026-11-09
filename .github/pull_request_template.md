## Qué cambia

<!-- Una o dos frases. -->

## IDs que cubre

<!-- Trazabilidad: RF-xx, RN-xx, CU-xx, RNF-xx. Ej.: RF-04, RN-03, CU-01 -->

## Checklist

- [ ] La documentación (`docs/`) se actualizó en este mismo PR si cambia una regla, un caso de uso o la base
- [ ] Si cambia la base: es una migración **nueva** en `supabase/migrations/` (no se editó una existente)
- [ ] Si cambia la API: se corrió `make gen-types` y se subieron los tipos
- [ ] `make lint` y `make test` pasan
