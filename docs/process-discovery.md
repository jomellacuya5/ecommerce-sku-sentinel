# Process Discovery: SKU Monitoring

Use these questions with the inventory planner, Amazon account manager, or e-commerce operator before changing the automation. Record the answers in the client handover document.

## Current process

1. Which report supplies stock, sales, cost, fee, and advertising data?
2. How often is that report refreshed and who owns its accuracy?
3. How does the expert decide a SKU needs a reorder or margin review today?
4. What happens after a SKU is flagged? Who places the order or changes pricing?

## Rules and exceptions

1. Does every SKU use the same lead time and safety-stock policy?
2. Are seasonal products, bundles, launches, or discontinued SKUs excluded?
3. Should zero sales mean no demand, missing data, or a new product?
4. Which costs belong in unit margin: marketplace fees, inbound freight, returns, taxes, discounts, or advertising?
5. What margin percentage needs an audit, and is it different by category?

## Handover acceptance criteria

The expert should approve the automation only after confirming that:

- the input columns map to the correct source fields;
- a known reorder-risk SKU is flagged correctly;
- a known low-margin SKU is flagged correctly;
- a zero-sales SKU does not cause a division error;
- an invalid input produces a visible failure log and alert;
- the action queue gives enough information for the next person to act.
