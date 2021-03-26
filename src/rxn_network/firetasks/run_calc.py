import json
from monty.json import MontyEncoder
from monty.serialization import dumpfn

from fireworks import explicit_serialize, FiretaskBase, FWAction
from rxn_network.firetasks.utils import get_logger, env_chk
from rxn_network.entries.entry_set import GibbsEntrySet
from rxn_network.reactions.reaction_set import ReactionSet


logger = get_logger(__name__)


@explicit_serialize
class RunEnumerators(FiretaskBase):
    required_params = ["enumerators", "entries"]

    def run_task(self, fw_spec):
        enumerators = self["enumerators"]
        entries = self.get("entries", None)

        if not entries:
            entries = fw_spec['entries']
        else:
            entries = entries["entries"]

        entries = GibbsEntrySet(entries)
        chemsys = "-".join(sorted(list(entries.chemsys)))
        target = enumerators[0].target
        added_elems = None
        if target:
            added_elems = entries.chemsys - {str(e) for e in Composition(
                target).elements}
            added_elems = "-".join(sorted(list(added_elems)))

        metadata = {}
        metadata["chemsys"] = chemsys
        metadata["enumerators"] = enumerators
        metadata["target"] = target
        metadata["added_elems"] = added_elems

        results = []
        for enumerator in enumerators:
            rxns = enumerator.enumerate(entries)
            results.extend(rxns)

        results = ReactionSet.from_rxns(rxns, entries)

        dumpfn(results, "rxns.json")
        dumpfn(metadata, "metadata.json")


@explicit_serialize
class RunNetwork(FiretaskBase):
    pass