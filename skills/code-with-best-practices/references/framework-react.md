Apply these practices whenever planning, writing, or reviewing React code.

## Contents

- Component Design
- Hooks Rules
- State
- Derived State and Memoization
- Effects Discipline
- Rendering and Keys
- Data Fetching
- Refs and DOM
- Errors

## Component Design

| Practice | Detail |
|---|---|
| Use function components only | Class components are legacy and hooks only work in function components, so a class adds a separate lifecycle model the rest of the codebase does not use. |
| One component per file, filename matching the component name | A `UserProfile.tsx` that exports `UserProfile` lets the debugger, error overlays, and hot reload name things correctly and makes the component trivial to locate. |
| Name components in PascalCase | JSX treats lowercase tags as HTML elements and capitalized tags as components, so `userProfile` would silently render as an unknown DOM tag. |
| Destructure props in the parameter list | Destructuring states the component's inputs up front and reads better than threading `props.` through the body. |
| Accept `children` for composition over passing JSX through named props | `children` is the idiomatic slot and keeps the parent agnostic about what it wraps, whereas a JSX-valued prop reinvents the same mechanism less clearly. |
| Treat `ref` as a regular prop (React 19) | `forwardRef` is no longer needed; accept `ref` in props directly. Reaching for `forwardRef` adds a wrapper the version no longer requires. |

## Hooks Rules

| Practice | Detail |
|---|---|
| Call hooks only at the top level | React identifies hooks by call order across renders, so a hook inside a loop, condition, or nested function shifts that order and corrupts state. Put the condition inside the hook, not around it. |
| Call hooks only from components or other hooks | Hooks rely on React's render context, which a plain utility function does not have, so calling one outside that context throws. |
| Prefix custom hooks with `use` | The prefix is what tells React and the linter to enforce the hook rules on the function; without it the rules go unchecked. |

## State

| Practice | Detail |
|---|---|
| Never mutate state in place | React detects changes by reference, so mutating an existing object or array (`user.name = 'x'`) leaves the reference unchanged and the re-render never happens. Create a new object: `{ ...user, name }`. |
| Use updater functions when the next state depends on the previous | `setCount(c => c + 1)` reads the latest value at apply time, whereas `setCount(count + 1)` captures a possibly stale value from the render's closure and drops batched updates. |
| Treat each render's state as an immutable snapshot | `setState` schedules the next render rather than changing the variable now, so reading the state right after setting it returns the old value. Do not expect it to update synchronously. |
| Lift state to the nearest common parent only when siblings share it | Shared state belongs at the lowest node that contains all its consumers; lifting higher than needed forces unrelated subtrees to re-render. |
| Pass a function to `useState` for expensive initial values | `useState(() => compute())` runs the initializer only on mount, while `useState(compute())` recomputes the value on every render and throws the result away. |
| Reach for `useReducer` when updates are multi-field or interdependent | A reducer centralizes related transitions in one tested function and gives a stable `dispatch` identity, which is clearer than juggling several `useState` setters. |

## Derived State and Memoization

| Practice | Detail |
|---|---|
| Compute derived values during render, not in state or effects | Filtered, sorted, or formatted data is a function of existing state, so storing it separately creates a second source of truth that drifts out of sync. Calculate it inline each render. |
| Do not mirror props into state | Initializing state from a prop captures the prop's first value and ignores later changes; read the prop directly, or key the component to reset it. |
| Add `useMemo` or `useCallback` only after profiling shows a real cost | Memoization has its own overhead and obscures the code, so applying it preemptively usually costs more than it saves. React 19's Compiler also auto-memoizes, removing most manual need. |
| Wrap a component in `React.memo` only when it re-renders often with unchanged props | `memo` compares props on every render, which is wasted work unless the component is genuinely expensive and its parent re-renders frequently with stable props. |

## Effects Discipline

| Practice | Detail |
|---|---|
| Use effects only to synchronize with external systems | Effects exist for subscriptions, timers, network, the DOM, and third-party libraries. Data that can be computed from props and state does not belong in an effect. |
| Never use an effect to transform data for rendering | Filtering or mapping in an effect runs an extra render pass and risks stale output; derive the value during render instead. |
| Handle user actions in event handlers, not effects | An effect that watches a state flag to react to a click runs later and on every matching change; the handler runs exactly when and where the action happens. |
| Return a cleanup function from every subscription, timer, or listener | Without cleanup the effect leaks and stacks duplicate subscriptions across re-renders and, in Strict Mode, double-invocation. |
| List every reactive value the effect reads in its dependency array | Props, state, and derived variables read inside the effect must be dependencies, or the effect runs against stale values from an old render. |
| Read the values you need before any `await` | Anything read after an `await` reflects a later render, not the one that started the effect, so capture required values synchronously first. |

## Rendering and Keys

| Practice | Detail |
|---|---|
| Give list items a stable unique key, never the array index | React matches elements across renders by key; an index key makes inserts and reorders remap state to the wrong item, while a stable id (`item.id`) preserves identity and DOM. |
| Do not create objects or functions inline in props to memoized children | A fresh `{}` or `() => {}` each render is a new reference, which defeats `memo` and forces the child to re-render. Hoist the constant or memoize it. |
| Use `useTransition` to keep urgent updates responsive during expensive ones | Marking a heavy state update as a transition lets typing and clicks render first instead of being blocked by the expensive work. |
| Use `useDeferredValue` to render an expensive view from a lagging copy of a value | It lets the urgent input update commit immediately while the expensive consumer catches up, avoiding a janky keystroke-by-keystroke render. |
| Split routes and below-the-fold trees with `lazy()` and `Suspense` | Code splitting at these boundaries shrinks the initial bundle so the first paint does not pay for screens the user has not reached. |

## Data Fetching

| Practice | Detail |
|---|---|
| Guard fetches in effects against race conditions | Set an `ignore` flag in the effect body and flip it in cleanup, then discard the response when ignored; otherwise a slow earlier request can overwrite a newer one. |
| Use `useOptimistic` for instant feedback on async actions | It shows the pending result immediately and reverts automatically on failure, which feels faster than waiting for the server round trip. |
| Unwrap promises and context with `use()` | `use()` reads a promise or context value and, unlike other hooks, may be called conditionally or in a loop, which suits Suspense-driven data flows. |
| Prefer a dedicated data layer over hand-rolled effect fetching for shared server state | Manual effect fetching reimplements caching, deduplication, and invalidation that a query library already handles correctly. |

## Refs and DOM

| Practice | Detail |
|---|---|
| Use `useRef` for imperative DOM work, not for rendered state | Refs are for focusing, scrolling, measuring, and animating. Mutating a ref does not trigger a re-render, so values the UI displays must live in state. |
| Use `useImperativeHandle` to expose a narrow API, not the raw node | Limiting the exposed surface to specific methods keeps callers from depending on the full DOM element and on internals you may change. |
| Use `useId` for generated ids that link elements | It produces ids that stay stable and unique across renders for pairing labels with inputs, instead of ad-hoc counters that can collide. |

## Errors

| Practice | Detail |
|---|---|
| Place Error Boundaries around independent sections | A boundary catches render errors in its subtree, so granular boundaries let one failed section degrade without taking down the whole app. |
| Catch event handler errors with `try/catch` | Error Boundaries only catch errors thrown during render, not in event handlers or async callbacks, which must handle their own failures. |
