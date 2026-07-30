# `-AT` layers: what they are and why the layer name must not be the classifier

## Answer

`-AT` = **ATtribute**. These layers hold the block attribute text (circuit, series, ID,
position) that belongs to fixtures inserted on the paired non-`-AT` layer. They are
overwhelmingly annotation — but not exclusively, and that exception is the trap.

## Evidence

Entity census across every `-AT` layer in the drawing:

| Entity type | Count | Share |
|---|---:|---:|
| `ATTRIB` | 641,705 | 99.55% |
| `ATTDEF` | 2,766 | 0.43% |
| `INSERT` | **726** | **0.11%** |
| `SEQEND` | 726 | 0.11% |
| `TEXT` | 1 | — |

Paired-layer comparison:

| Layer | Entities | Type mix |
|---|---:|---|
| `EL-TAXICL` | 9,650 | 4,783 INSERT + 4,783 SEQEND + 84 misc |
| `EL-TAXICL-AT` | 126,276 | 126,040 ATTRIB + 236 ATTDEF, **zero INSERT** |
| `ADB_TAXICL` | 5,927 | 2,932 INSERT + 2,932 SEQEND + 63 misc |
| `ADB_TAXICL-AT` | 76,414 | 76,250 ATTRIB + 164 ATTDEF, **zero INSERT** |

The INSERT/SEQEND pairing is the giveaway. In DXF, a block insertion that carries
attributes is written as `INSERT` → n × `ATTRIB` → `SEQEND`. Every fixture has exactly
one INSERT and one SEQEND; the drafter put the INSERT on the asset layer and pushed the
ATTRIBs onto a parallel `-AT` layer. 126,040 ÷ 4,783 = **26.4 attributes per taxiway
centreline light**.

## The exception that matters

726 INSERTs were drafted onto `-AT` layers:

| `-AT` layer | INSERTs | Blocks |
|---|---:|---|
| `EL-APPROACH-AT` | 330 | `APP-el_c` (300), `ASR-el_r` (30) |
| `EL-LEAD-IN-AT` | 319 | `TCL-s_gb` (176), `TCL-s_yb` (143) |
| `EL-FLASHING-AT` | 42 | `SFL-el` |
| `EL-STOPBAR-AT` | 20 | `STB-in` |
| `ADB_TAXIWAY EDGE-AT` | 15 | `TWE-in` |

**These are real, distinct fixtures, not duplicates.** Nearest-neighbour test against
every fixture on the paired non-`-AT` layer: **0 of 726** fall within 0.25 m, and none
within 5 m. Their nearest neighbour of any type is a different asset entirely (handhole,
transformer pit, taxiway edge) at 3–14 m. The `EL-LEAD-IN-AT` string is `TCL-s_gb` /
`TCL-s_yb` alternating at ~15 m spacing — a textbook taxiway centreline run, drafted on
the wrong layer.

## Consequences

| Rule | Effect |
|---|---|
| Exclude all `-AT` layers | Loses **726 real fixtures** |
| Include all `-AT` entities | Adds **644,471 text records** counted as assets |
| **Filter on entity type = `INSERT`** | **Correct** |

The extraction pipeline (`rebuild.py`) has always filtered on `INSERT`, so the fixture
count of 33,720 was never affected by this. What was affected was `asset_type`: the old
layer-name lookup left all 726 as `Unclassified`, alongside 3,458 others.

## The general rule

Layer name is the drafter's *intent*. Entity type is the drawing's *structure*. When the
two disagree, structure wins — a drafter can put anything on any layer, but an `ATTRIB`
is never a light fitting and an `INSERT` always is a placed object.

Apply the same reasoning before excluding any layer by name pattern. Check the entity
census first.
