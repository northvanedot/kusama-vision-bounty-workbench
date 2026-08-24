# MultiAssetBounties Child Bounty Runbook — Kusama Asset Hub

Step-by-step flow for creating, funding, activating, awarding and finalizing a
MultiAssetBounties child bounty on **Kusama Asset Hub**, using a curator multisig and a
Governance proxy.

Written to cover all three Kusama Vision bounties. The procedure is identical for each —
only the parameters in the table below change. Substitute them once at the start and the
rest of the document reads straight through.

| id | bounty | pot (23 Aug 2026) | child bounties so far |
|---|---|---|---|
| `0` | Proof of Personhood | 159,918.129 DOT | 2 |
| `1` | Art & Social Experiments | 105,128.979 DOT | 4 |
| `2` | Zero-Knowledge & Cryptography | 135,622.729 DOT | 2 |

Balances and counts read from Kusama Asset Hub on 23 Aug 2026. They move — the pot grows
with monthly top-ups, so re-check rather than trusting the figures above.

> Important: all steps in this document are for **Kusama Asset Hub**. Do not use Polkadot Asset Hub or the Kusama Relay Chain for these steps unless explicitly stated.

---

## Roles and Terminology

### Bounty parameters

Every step below is written against these three names. Pick the bounty you are working on
and read its column; the workbench fills them in automatically for whichever bounty and
child you have selected.

| | `0` — Proof of Personhood | `1` — Art & Social Experiments | `2` — Zero-Knowledge & Cryptography |
|---|---|---|---|
| `BOUNTY_ID` | `0` | `1` | `2` |
| `CURATOR_ACCOUNT` | `HfMgvo7Lfuymg9sxii2H747rXdts5be6UfLPp6kXS4cNE9u` | `HyfBoVzPkikGdDv5P9pNoMkHrQJ5LvktdXwiv9RntbrTHi4` | `DVYbCSWbNfNxA2DXK1TUJSUaBYZVyeVq6AEvmp98S2nn3LH` |
| `CURATOR_MULTISIG` | `FhDqdZBwWH16Auzttnc4hurJNVHNZYguMGPWxY2Bjzzxt6G` | `HNAgeYNFWJeNXBoe5Nf5KHLY5q2hp8X2UJNJjFGnrU8YYjw` | `D3LkMK27GeTV924MVcHJHDPwuHrk1jovzvAKKAoh3SJJHed` |

Curator accounts read from `multiAssetBounties.bounties(BOUNTY_ID)`; multisigs read from
`proxy.proxies(CURATOR_ACCOUNT)`, taking the delegate with proxy type `7` (Governance).
Both queried on Kusama Asset Hub, 23 Aug 2026. Bounty 0's entries match the values this
document was originally written with, which is what validates the method for the other two.

Every curator account also carries a second delegate with proxy type `0` (Any):
`EFuprYL5sShF5qao4F9hVRrkbutFeoAgn4HHehq4Rkx3ahm`. It is the same account across all three
bounties and holds unrestricted authority over each curator account — worth knowing about,
not something curators act through.

Where this document says a transaction can be submitted by a **curator multisig
signatory**, it means any one of that bounty's signatories can initiate or submit it.
The operation still needs the bounty's threshold in approvals before it executes.


### Governance proxy

The curator multisig uses a **Governance proxy** to act on behalf of the parent curator/proxied account.

When this document says:

```text
curator multisig via Governance proxy
```

it means the operation should be structured as:

```text
curator multisig
  → proxy.proxy
      real: <CURATOR_ACCOUNT>
      force_proxy_type: Governance
      call: <nested call>
```

---

## Pre-check — Confirm Parent Bounty Status and Funds

Before creating a child bounty, confirm the parent bounty exists, is active, uses the expected asset, and has enough allocated value.

For this flow, the parent bounty is:

```text
parent_bounty_id: <BOUNTY_ID>
```

### Check parent bounty storage

Go to:

```text
Polkadot.js → Kusama Asset Hub → Developer → Chain state
```

Query:

```text
multiAssetBounties.bounties(<BOUNTY_ID>)
```

Expected parent bounty state:

```text
assetKind: DOT on Kusama Asset Hub
value: <current allocation — see note below>
status: Active
curator: <CURATOR_ACCOUNT>
```

`value` is the amount **allocated to this parent bounty**, not the pot balance. A freshly
created bounty starts at `10,000,000,000` (1 DOT) and stays there until someone calls
`increaseValue`. So a low `value` alongside a six-figure pot is the normal starting state,
not a fault. Compare `value` against the child bounty you intend to create; if it is
lower, run the `increaseValue` pre-check below first.

The parent bounty asset should show:

```text
assetKind:
  V5:
    location:
      parents: 0
      interior: Here
    assetId:
      parents: 2
      interior:
        X1:
          GlobalConsensus: Polkadot
```

This represents DOT as a foreign asset on Kusama Asset Hub.

### Confirm enough value

The parent bounty value is:

```text
10,000,000,000
```

For DOT with 10 decimals, this is:

```text
1 DOT
```

The test child bounty value is:

```text
1,000,000,000
```

For DOT with 10 decimals, this is:

```text
0.1 DOT
```

So the parent bounty has enough allocated value for a `0.1 DOT` child bounty.

Do not create a child bounty if:

```text
- the parent bounty does not exist
- the parent bounty is not Active
- the asset is not the expected DOT asset
- the parent bounty value is less than the intended child bounty value
- the curator is not the expected parent curator/proxied account
```

Note: a larger DOT balance in a pot or derived account does not necessarily mean it is spendable by a specific parent bounty. Treat the parent bounty `value` as the spendable allocation for that bounty.

---


## Step 0 — Increase the Parent Bounty Value

Run this step when the parent bounty's recorded `value` is lower than the child bounty you
intend to create. Skip it when `value` already covers the amount.

This is the normal path after a monthly top-up: DOT arriving in the bounty account does not
raise `value` on its own. The runtime documentation is explicit that the call exists
to "register funds that were transferred into the bounty account out-of-band
(e.g. recurring external top-ups), so they become available to award or to allocate to
child bounties."

### 0.1 The call

Verified against Kusama Asset Hub runtime metadata, 23 Aug 2026:

```text
multiAssetBounties.increase_value(
  parent_bounty_id: BountyIndex,     // <BOUNTY_ID>
  amount:           T::Balance       // the INCREMENT, not the new total
)
```

`amount` is added to the existing `value`. It is not a new total. To take a bounty sitting
at 1 DOT up to 4,000 DOT of headroom, pass `amount = 3,999 DOT` — or pass 4,000 and accept
that `value` ends at 4,001.

DOT on Kusama Asset Hub has 10 decimals:

```text
1 DOT      = 10,000,000,000
4,000 DOT  = 40,000,000,000,000
```

### 0.2 Before you call it

Four things the runtime enforces or warns about:

```text
- Origin must be signed by the bounty curator.
- The bounty must be in the Active state.
- amount must be greater than 0.
- value can only be increased, never decreased.
```

Two consequences worth understanding before submitting:

**The curator pays an additional deposit.** The curator deposit is re-evaluated against the
new value and the difference is collected from the curator account. Confirm
`<CURATOR_ACCOUNT>` holds enough free balance to cover it, or the call fails.

**The call does not check the bounty account actually holds the funds.** It only updates the
recorded number. You can raise `value` above the real balance and the failure will surface
later, at award time, not here. Always check the pot balance covers the new value yourself —
see the pre-check above.

Because the increase is irreversible, raise `value` by what the child bounty needs rather
than by the whole pot.

### 0.3 Who calls it, and how

The origin must be the bounty curator, so this goes through the same proxy path as every
other curator action:

```text
curator multisig
  → proxy.proxy
      real: <CURATOR_ACCOUNT>
      force_proxy_type: Governance
      call: multiAssetBounties.increase_value(<BOUNTY_ID>, amount)
```

Initiate from any signatory; the operation needs the bounty's threshold in approvals before
it executes.

### 0.4 Confirm it landed

```text
multiAssetBounties.bounties(<BOUNTY_ID>)
```

Check `value` has risen by `amount` and `status` is still `Active`. Only then continue to
Step 1.

---

## Step 1 — Create and Register the Metadata Preimage

Before creating a child bounty, create a metadata preimage on **Kusama Asset Hub**. The `metadata` field in `fundChildBounty` is an `H256` hash that points to an on-chain preimage.

The preimage must be created on **Kusama Asset Hub**, not the Kusama Relay Chain, because the `multiAssetBounties` pallet is running on Kusama Asset Hub.

### 1.1 Create the metadata JSON

Example metadata:

```json
{"title":"Test child bounty #2","description":"Second test of the MultiAssetBounties child bounty flow using parent curator.","amount":"0.1 DOT","parent_bounty_id":<BOUNTY_ID>,"curator":"parent"}
```

Keep the metadata simple and descriptive. Any change to spacing, punctuation, or text creates a different preimage hash.

### 1.2 Submit the preimage

Go to:

```text
Polkadot.js → Kusama Asset Hub → Developer → Extrinsics
```

Use:

```text
Pallet: preimage
Call: notePreimage(bytes)
Submit from: any curator multisig signatory
```

Paste the metadata JSON into the `bytes` field.

Use:

```text
Submit Transaction
```

Do not use `Submit Unsigned`.

### 1.3 Wait for finalization

After submitting, wait until the transaction is:

```text
Finalized
```

If it is only `Ready` or spinning, wait or check whether the wallet still needs approval.

### 1.4 Confirm the preimage exists

Go to:

```text
Polkadot.js → Kusama Asset Hub → Developer → Chain state
```

Query:

```text
preimage.preimageFor((H256, u32))
```

For the example metadata above, use:

```text
H256:
<PREIMAGE_HASH>

u32:
185
```

Expected result:

```text
Some(0x...)
```

or a returned bytes value.

If it returns:

```text
<none>
```

the preimage is not stored on-chain and should not be used yet.

### 1.5 Use the preimage hash as metadata

Once confirmed, use the preimage hash as the `metadata` value in the child bounty creation call:

```text
metadata:
<PREIMAGE_HASH>
```

Important: do not use the `encoded call hash` from the `notePreimage` form. The metadata hash must be the actual preimage hash confirmed by `preimage.preimageFor`.

---

## Step 2 — Create/Fund the Child Bounty

After the metadata preimage is confirmed on Kusama Asset Hub, create the child bounty using the curator multisig through the Governance proxy.

The curator multisig does **not** call `fundChildBounty` directly. The correct structure is:

```text
curator multisig
  → proxy.proxy
      → multiAssetBounties.fundChildBounty
```

### 2.1 Confirm the next child bounty ID

Before creating a new child bounty, check how many child bounties already exist under the parent bounty.

Go to:

```text
Polkadot.js → Kusama Asset Hub → Developer → Chain state
```

Query:

```text
multiAssetBounties.totalChildBountiesPerParent(0)
```

If the result is:

```text
1
```

then the next child bounty will likely be:

```text
child_bounty_id: 1
```

### 2.2 Start the multisig operation in Nova Spektr

In Nova Spektr, create a new multisig operation.

Use:

```text
Network: Kusama Asset Hub
Submit from: PoP Bounty Team Kusama Vision multisig
Initiator: any curator multisig signatory
```

### 2.3 Build the outer proxy call

Select:

```text
Pallet: proxy
Call: proxy
```

Set:

```text
real:
<CURATOR_ACCOUNT>

force_proxy_type:
Governance
```

This means the curator multisig is acting through its Governance proxy over the parent bounty curator/proxied account.

### 2.4 Build the nested child bounty call

Inside the `call` field of `proxy.proxy`, select:

```text
Pallet: multiAssetBounties
Call: fundChildBounty
```

Use:

```text
parent_bounty_id: <BOUNTY_ID>
value: <CHILD_VALUE>
metadata: <CHILD_METADATA>
curator: null
```

The value:

```text
1,000,000,000
```

represents `0.1 DOT` for the DOT asset, assuming 10 decimals.

In some UIs, the balance field may display as:

```text
0.001 KSM
```

That is acceptable only if the operation preview shows the raw value as:

```text
"value": "<CHILD_VALUE>"
```

Do not submit if the preview shows:

```text
"value": "0"
```

or a much larger value.

### 2.5 Use parent curator to reduce steps

Set:

```text
curator: null
```

This makes the child bounty use the parent curator by default.

That reduces the flow because the child bounty should move from:

```text
FundingAttempted → Active
```

after `checkStatus`.

If a separate curator is assigned, the flow would be:

```text
FundingAttempted → Funded → acceptCurator → Active
```

### 2.6 Review the operation preview

The operation should look like this:

```json
{
  "method": "proxy",
  "section": "proxy",
  "args": {
    "real": "<CURATOR_ACCOUNT>",
    "force_proxy_type": "Governance",
    "call": {
      "method": "fundChildBounty",
      "section": "multiAssetBounties",
      "args": {
        "parent_bounty_id": "<BOUNTY_ID>",
        "value": "<CHILD_VALUE>",
        "metadata": "<PREIMAGE_HASH>",
        "curator": null
      }
    }
  }
}
```

Do not submit if:

```text
force_proxy_type: null
```

It must be:

```text
force_proxy_type: Governance
```

### 2.7 Submit and collect approvals

Submit the operation from any curator multisig signatory.

After one signatory submits, the operation shows a partial signature count. The remaining
signatories must approve before the operation executes — how many depends on this bounty's
multisig threshold, which the signing UI displays.

### 2.8 Confirm the child bounty was created

After the multisig reaches the threshold and executes, go to:

```text
Polkadot.js → Kusama Asset Hub → Developer → Chain state
```

Query:

```text
multiAssetBounties.totalChildBountiesPerParent(0)
```

Expected result:

```text
2
```

Then query:

```text
multiAssetBounties.childBounties(<BOUNTY_ID>, <CHILD_ID>)
```

Expected result:

```text
parentBounty: <BOUNTY_ID>
value: <CHILD_VALUE>
metadata: <CHILD_METADATA>
status: FundingAttempted
curator: <CURATOR_ACCOUNT>
```

This confirms the child bounty was created successfully and is ready for the funding status check.

---

## Step 3 — Check Funding Status

After the multisig operation executes and the child bounty is created, the child bounty will usually start in this state:

```text
FundingAttempted
```

This means the bounty record exists and the payment/funding attempt has been initiated, but the funding status has not yet been finalized.

### 3.1 Confirm the child bounty state

Go to:

```text
Polkadot.js → Kusama Asset Hub → Developer → Chain state
```

Query:

```text
multiAssetBounties.childBounties(<BOUNTY_ID>, <CHILD_ID>)
```

Expected result before checking status:

```text
parentBounty: <BOUNTY_ID>
value: <CHILD_VALUE>
metadata: <CHILD_METADATA>
status: FundingAttempted
```

### 3.2 Run checkStatus

Go to:

```text
Polkadot.js → Kusama Asset Hub → Developer → Extrinsics
```

Use:

```text
Pallet: multiAssetBounties
Call: checkStatus
```

Set:

```text
parentBountyId: <BOUNTY_ID>
childBountyId: Some(1)
```

Then submit the transaction from any curator multisig signatory.

This call does not need to be submitted through the curator multisig. It can be submitted by any signed account.

### 3.3 Confirm the updated state

After `checkStatus` finalizes, query again:

```text
multiAssetBounties.childBounties(<BOUNTY_ID>, <CHILD_ID>)
```

Expected result:

```text
status: Active
curator: <CURATOR_ACCOUNT>
```

### 3.4 Why it becomes Active

Because the child bounty was created with:

```text
curator: null
```

it uses the parent curator:

```text
<CURATOR_ACCOUNT>
```

That means the flow skips the separate curator acceptance step.

The expected transition is:

```text
FundingAttempted → Active
```

If a separate curator had been assigned, the transition would usually be:

```text
FundingAttempted → Funded → acceptCurator → Active
```

---

## Step 4 — Award the Child Bounty to the Beneficiary

After the child bounty is `Active`, it can be awarded to a beneficiary.

For this test, the active child bounty is:

```text
parent_bounty_id: <BOUNTY_ID>
child_bounty_id: 1
value: <CHILD_VALUE>
status: Active
curator: <CURATOR_ACCOUNT>
```

Because the curator is the proxied parent curator account, the award must be executed through the curator multisig using the Governance proxy.

The correct structure is:

```text
curator multisig
  → proxy.proxy
      → multiAssetBounties.awardBounty
```

### 4.1 Beneficiary account

The beneficiary provided this Kusama/Asset Hub address:

```text
FfDhYNF9pStknnmRKuipNSgpjeknhin45GKjHejFArjnKZt
```

This decodes to the following 32-byte account ID:

```text
0x8871579fd0c679ace59d1e62cda57c339ed883de8357a49f2a4dace411478327
```

This is the value that must be used in the `AccountId32` field.

### 4.2 Beneficiary existential deposit note

DOT on Kusama Asset Hub is a sufficient foreign asset, so the beneficiary does not need an existing KSM existential deposit just to receive the DOT payout.

However, the beneficiary may still need fee-paying capability later to move or manage the received funds.

### 4.3 Build the outer proxy call

In Nova Spektr, create a new multisig operation.

Use:

```text
Network: Kusama Asset Hub
Submit from: PoP Bounty Team Kusama Vision multisig
Initiator: any curator multisig signatory
```

Select:

```text
Pallet: proxy
Call: proxy
```

Set:

```text
real:
<CURATOR_ACCOUNT>

force_proxy_type:
Governance
```

### 4.4 Build the nested award call

Inside the `call` field of `proxy.proxy`, select:

```text
Pallet: multiAssetBounties
Call: awardBounty
```

Set:

```text
parent_bounty_id: <BOUNTY_ID>
child_bounty_id: 1
```

For the beneficiary, use:

```text
beneficiary: V5

location:
  parents: 0
  interior: Here

accountId:
  parents: 0
  interior: X1
    AccountId32:
      network: null
      id: 0x8871579fd0c679ace59d1e62cda57c339ed883de8357a49f2a4dace411478327
```

The `location: Here` means the payment is made on Kusama Asset Hub.

The `accountId` is the beneficiary account that will receive the payout.

### 4.5 Nova/Spektr beneficiary encoding issue

During testing, Nova/Spektr sometimes defaulted the beneficiary `AccountId32` to:

```text
0x0000000000000000000000000000000000000000000000000000000000000000
```

or shifted the account ID to:

```text
0x0000008871579f...
```

Do not submit the operation if the beneficiary is zero or shifted.

The correct beneficiary ID must start with:

```text
0x8871579f...
```

and must be the full value:

```text
0x8871579fd0c679ace59d1e62cda57c339ed883de8357a49f2a4dace411478327
```

### 4.6 Correct raw call data

The corrected proxy-wrapped award call data is:

```text
0x2a0000e104b438e7893a9f9cbc59e7d057d61a85ed1b88e3a0ebc59733cb89637a5e7c01076205000101000000050000000101008871579fd0c679ace59d1e62cda57c339ed883de8357a49f2a4dace411478327
```

This decodes to:

```text
proxy.proxy
  real: <CURATOR_ACCOUNT>
  force_proxy_type: Governance
  call:
    multiAssetBounties.awardBounty
      parent_bounty_id: <BOUNTY_ID>
      child_bounty_id: 1
      beneficiary:
        V5
          location: Here
          accountId:
            AccountId32
              network: null
              id: 0x8871579fd0c679ace59d1e62cda57c339ed883de8357a49f2a4dace411478327
```

### 4.7 Review before submitting

Before submitting, confirm:

```text
method: proxy
section: proxy
real: <CURATOR_ACCOUNT>
force_proxy_type: Governance
nested call: multiAssetBounties.awardBounty
parent_bounty_id: <BOUNTY_ID>
child_bounty_id: 1
beneficiary id: 0x8871579f...8327
```

Do not submit if:

```text
beneficiary id: 0x000000...
```

or:

```text
beneficiary id: 0x000000887...
```

### 4.8 Submit and collect approvals

Submit the operation from any curator multisig signatory.

After one signatory submits, the remaining signatories must approve before the operation
executes — how many depends on this bounty's multisig threshold, which the signing UI
displays.

After execution, the child bounty status should move from:

```text
Active
```

to something like:

```text
PayoutAttempted
```

---

## Step 5 — Confirm Award Execution and Finalize Payout

After the `awardBounty` multisig operation is submitted, it must receive enough approvals before execution.

The award operation follows this structure:

```text
curator multisig
  → proxy.proxy
      → multiAssetBounties.awardBounty
```

Once the multisig reaches the threshold, the award call executes and the child bounty should move from:

```text
Active
```

to:

```text
PayoutAttempted
```

### 5.1 Check the pending multisig operation

To check the pending multisig in Polkadot.js, go to:

```text
Polkadot.js → Kusama Asset Hub → Developer → Chain state
```

Query:

```text
multisig.multisigs(AccountId32, [u8;32])
```

Use:

```text
AccountId32:
<CURATOR_MULTISIG>
```

This is the curator multisig account.

For the call hash, use the award call hash from Nova/Spektr or Polkadot.js decode.

Leave the optional block hash field blank.

Expected result while pending:

```text
Some(...)
```

The result should show details such as the depositor, deposit, timepoint, and approvals.

If the result is:

```text
None
```

then one of these may be true:

```text
- the call hash is incorrect
- the operation already executed
- the operation failed or was removed
- the wrong network is selected
```

### 5.2 Confirm the child bounty status

After the multisig reaches threshold and executes, check the child bounty state.

Go to:

```text
Polkadot.js → Kusama Asset Hub → Developer → Chain state
```

Query:

```text
multiAssetBounties.childBounties(<BOUNTY_ID>, <CHILD_ID>)
```

Expected result after successful award:

```text
status: PayoutAttempted
```

This means the award call executed and the payout process has started.

### 5.3 Finalize/check the payout

Once the child bounty shows `PayoutAttempted`, submit:

```text
Polkadot.js → Kusama Asset Hub → Developer → Extrinsics
```

Use:

```text
Pallet: multiAssetBounties
Call: checkStatus
```

Set:

```text
parentBountyId: <BOUNTY_ID>
childBountyId: Some(1)
```

This does not need to go through the curator multisig. It can be submitted by any curator multisig signatory.

### 5.4 Confirm final state

After `checkStatus` finalizes, query again:

```text
multiAssetBounties.childBounties(<BOUNTY_ID>, <CHILD_ID>)
```

If the payout succeeded, the child bounty may be removed from storage.

Possible final results:

```text
None / no child bounty found
```

or a state showing the payout has completed.

If the bounty still shows:

```text
PayoutAttempted
```

then the payout may still need another status check or further review.

### 5.5 Confirm beneficiary received funds

Check the beneficiary account on Kusama Asset Hub:

```text
FfDhYNF9pStknnmRKuipNSgpjeknhin45GKjHejFArjnKZt
```

Underlying AccountId32:

```text
0x8871579fd0c679ace59d1e62cda57c339ed883de8357a49f2a4dace411478327
```

Confirm the beneficiary received the expected payout amount:

```text
0.1 DOT
```

on Kusama Asset Hub.

---

## Common Issues and Notes

### Priority is too low

If a transaction fails with:

```text
1014: Priority is too low
```

there is likely another transaction from the same signer with the same nonce still in the transaction pool.

Wait a few minutes, refresh the app/wallet, and check whether the earlier transaction finalized or dropped before submitting again.

### Preimage returns `<none>`

If `preimage.preimageFor(hash, length)` returns:

```text
<none>
```

do not use that metadata hash yet. The preimage is not stored on-chain.

### Wrong network

Always confirm the top-left network is:

```text
Kusama Asset Hub
```

Do not accidentally use:

```text
Polkadot Asset Hub
Kusama Relay Chain
Polkadot Relay Chain
```

### Parent bounty value vs pot balance

Use:

```text
multiAssetBounties.bounties(<BOUNTY_ID>)
```

as the main source of truth for parent bounty allocation/status.

A separate pot or derived account may hold more DOT, but that does not automatically mean a specific parent bounty can spend it.
