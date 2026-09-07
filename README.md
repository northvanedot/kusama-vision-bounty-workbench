# Kusama Vision Bounty Workbench

A single static page for curators of the three Kusama Vision bounties. It fills the
child-bounty runbook in from Kusama Asset Hub for whichever bounty and child you select —
live state for children that exist, archive state for those that have settled.

**→ https://northvanedot.github.io/kusama-vision-bounty-workbench/**

Built by a curator of the Proof of Personhood bounty. Not an official Kusama Vision
publication.

## What it does

- Live pot balance, recorded `value` and headroom for bounties `0`, `1` and `2`
- Every child bounty with its value and status, decoded from
  `pallet_multi_asset_bounties::ChildBounty` in the live runtime metadata
- Clicking a child jumps the runbook to the step that child is actually at
- Runbook placeholders fill in from chain for the selected bounty and child
- Children that have settled are listed and rebuilt from archive state — value, metadata,
  beneficiary, and the block they were removed at
- The metadata preimage behind every child is read back, so a payment shows what it was for
- Step 1 composes new metadata, hashes it locally and checks whether it is already registered
- For a payout still unsettled, checks whether the beneficiary's balance actually moved in
  the block it was attempted

## What it does not do

**It never signs, and holds no keys.** There is no backend and no wallet connection. Every
figure is a chain query you can repeat in Polkadot.js.

Call data is built in-page for the simple calls — `increaseValue`, `checkStatus`,
`acceptCurator`, `unassignCurator`, `retryPayment`, `closeBounty`. The SCALE encoding was
verified byte-for-byte against `@polkadot/api` output for the same arguments.

`fundBounty`, `fundChildBounty`, `proposeCurator` and `awardBounty` are deliberately **not**
built here. They take `MultiAddress`, `H256` and `VersionedLocatableAccount` arguments —
exactly the argument class the runbook documents an encoding bug for. Build those in Nova Spektr
(the desktop wallet — not Nova Wallet) under **Custom operation → Build an operation**, or in
Polkadot.js Apps, where the UI encodes them from runtime metadata. That dialog also has a
**Paste** tab that takes raw call data, so the hex this page emits goes straight in.

Steps 2 and 4 list every argument those calls need, ready to copy — the page just won't
encode them.

## Before you sign anything

Decode the call data in **Polkadot.js Apps → Developer → Extrinsics → Decode** and confirm it
matches the call and arguments the page displays. The page proposes; Polkadot.js Apps confirms.
Do not sign on this tool's word alone.

## Rebuilding

The page embeds the runbook so it works offline. To regenerate after editing
`child-bounty-runbook.md`:

```bash
python3 build.py
```

## Verifying the encoder yourself

```js
import { ApiPromise, WsProvider } from '@polkadot/api';
const api = await ApiPromise.create({ provider: new WsProvider('wss://kusama-asset-hub-rpc.polkadot.io') });
console.log(api.tx.multiAssetBounties.increaseValue(0, 39990000000000n).method.toHex());
// 0x6209000b009cbee55e24 — compare against what the page emits for the same arguments
```

## Upstream references

- [`pallet-multi-asset-bounties` **0.7.0** rust docs](https://docs.rs/pallet-multi-asset-bounties/0.7.0/pallet_multi_asset_bounties/pallet/enum.Call.html)
  — this is the version Kusama Asset Hub actually runs. The chain reports
  `spec_version 2003002`, which is polkadot-fellows/runtimes `v2.3.2`, and that release's
  `Cargo.lock` pins `pallet-multi-asset-bounties 0.7.0` from crates.io. [T]

  Read the version, not just the crate. `polkadot-sdk` master is already at `1.0.0`, and
  docs for it are on docs.rs as `pezpallet-multi-asset-bounties` — a third party's
  republish of the newer source. Those docs describe code Kusama is not running yet.
- [Multi-Asset Bounties Now Live on Westend: Testing and Roadmap](https://forum.polkadot.network/t/multi-asset-bounties-now-live-on-westend-testing-and-roadmap/16899) —
  Polkadot Forum, background and roadmap.

This runbook is the failure-mode companion to those: what we hit running the flow on
Kusama Asset Hub, not a substitute for the pallet docs.

## Licence

MIT
