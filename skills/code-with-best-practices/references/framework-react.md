Apply these practices whenever planning, writing, or reviewing React code. Targets React 19 (version-specific items are flagged). Generic clean-code and naming rules live in CLAUDE.md; this reference is the React-specific, version-current, and easy-to-get-wrong material. On conflict, the project's own conventions win.

## Contents

- [Purity and the Rules of React](#purity-and-the-rules-of-react)
- [Hooks rules](#hooks-rules)
- [State and colocation](#state-and-colocation)
- [Derived state, not effects](#derived-state-not-effects)
- [When NOT to use an Effect](#when-not-to-use-an-effect)
- [Effect discipline (when you do need one)](#effect-discipline-when-you-do-need-one)
- [Memoization with a measured reason](#memoization-with-a-measured-reason)
- [Server vs Client Components (RSC)](#server-vs-client-components-rsc)
- [React 19 features](#react-19-features)
- [Rendering, keys, refs, errors](#rendering-keys-refs-errors)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Purity and the Rules of React

| Practice | Detail |
|---|---|
| Render must be pure | A component must return the same JSX for the same props, state, and context. No network calls, no timers, no subscriptions, no DOM writes, no logging side effects during render: those are bugs that Strict Mode's double-render surfaces. |
| Do not mutate props, state, or hook arguments | They are immutable snapshots for a single render. Mutating an existing object (`user.name = x`, `arr.push(...)`) does not trigger a re-render and corrupts other renders. Build a new value: `{ ...user, name }`. |
| You may mutate only what you just created in this render | A fresh local object or array made during render is fine to build up before returning. Anything from a prior render, props, or a hook is off-limits. |
| Do not mutate a value after passing it to JSX | Mutate before the JSX is created; once handed to JSX it is frozen for that render. |
| Never call a component as a plain function | Use `<Comp />`, not `Comp()`. Calling it directly skips React's render machinery (hooks, state, reconciliation) and breaks the hook rules. |
| Never pass a hook as a value | Hooks are called at the top level of a component or another hook, never stored, forwarded, or invoked dynamically. |

## Hooks rules

| Practice | Detail |
|---|---|
| Call hooks only at the top level | React identifies hooks by call order across renders, so a hook inside a loop, condition, or nested function (or after an early `return`) shifts that order and corrupts state. Put the condition inside the hook, not around it. |
| Call hooks only from components or custom hooks | Hooks need React's render context, which a plain utility lacks; calling one outside throws. |
| Prefix custom hooks with `use` | The prefix is what tells React and the linter to enforce the hook rules; without it they go unchecked. |
| `use()` is the one exception (19) | `use(promise)` and `use(context)` may be called conditionally or in a loop, unlike every other hook, which suits Suspense and early-return reads. |

## State and colocation

| Practice | Detail |
|---|---|
| Colocate state at the lowest component that needs it | Place state as close to where it is read as possible; lifting higher than necessary makes every update re-check unrelated subtrees and scatters the logic away from its use. |
| Lift only to the nearest common parent of all consumers | When siblings share state, lift to their shared parent and no higher. When that causes prop-drilling, put a context provider near those components, not at the app root. |
| Never mutate state in place | React diffs by reference; mutating leaves the reference unchanged and skips the re-render. Return a new object or array. |
| Use updater functions when next state depends on previous | `setCount(c => c + 1)` reads the latest value at apply time; `setCount(count + 1)` captures a possibly stale closure value and drops batched updates. |
| Treat each render's state as an immutable snapshot | `setState` schedules the next render; it does not change the variable now, so reading state right after setting it returns the old value. |
| Pass a function to `useState` for expensive initial values | `useState(() => compute())` runs the initializer only on mount; `useState(compute())` recomputes every render and discards it. |
| Reach for `useReducer` when updates are multi-field or interdependent | A reducer centralizes related transitions in one testable function and gives a stable `dispatch`, clearer than juggling several setters, and it shrinks effect dependency lists. |

## Derived state, not effects

| Practice | Detail |
|---|---|
| Compute derived values during render | Filtered, sorted, or formatted data is a function of existing state. Calculate it inline each render instead of storing a second copy that drifts out of sync. |
| Do not mirror props into state | Initializing state from a prop captures only its first value and ignores later changes. Read the prop directly, or reset with a `key`. |
| Reset state on identity change with a `key`, not an effect | `<Profile userId={id} key={id} />` makes React treat each id as a fresh component and discard old state, replacing an effect that watches `userId` to clear fields. |
| Adjust state during render when a prop changes, rarely | When you truly must, compare against a stored previous value and call the setter during render (`if (items !== prevItems) { setPrevItems(items); setSelection(null); }`); React reruns before painting. Prefer `key` or derivation first. |

## When NOT to use an Effect

Effects are an escape hatch for synchronizing with external systems. If no external system is involved, you almost certainly do not need one.

| Anti-pattern | Do instead |
|---|---|
| Effect that sets state from props/state | Compute the value during render. |
| Effect caching an expensive calculation | `useMemo(() => getFiltered(items, filter), [items, filter])`. |
| Effect that runs logic in response to a click or submit | Put it in the event handler. By the time an effect runs you no longer know what the user did. |
| POST or notification fired by watching a state flag | Call it directly from the handler that caused it. |
| Chains of effects each triggering the next setState | Calculate all the next state in the one event handler; chains cause extra render passes and cascades. |
| Effect calling `onChange(value)` to notify the parent | Update local state and call `onChange` together in the same handler; React batches them into one pass. |

## Effect discipline (when you do need one)

| Practice | Detail |
|---|---|
| Each render has its own effect closing over that render's values | An effect captures the props and state of the render that defined it, not the latest. Stale values mean a dishonest dependency array, not a reason to omit deps. |
| List every reactive value the effect reads | Props, state, context, and derived locals read inside must be dependencies, or the effect runs against stale values. Remove a dependency by removing the read (functional updater, `useReducer`), not by lying. |
| Return a cleanup from every subscription, timer, or listener | Cleanup runs before the next effect and on unmount, capturing its own render's values. Without it, subscriptions stack and Strict Mode's dev double-invoke leaks. |
| Guard fetches against races | Set an `ignore` flag in the effect, flip it in cleanup, and discard the response when ignored, so a slow earlier request cannot overwrite a newer one. Read values before any `await`. |
| Subscribe to external stores with `useSyncExternalStore` | Purpose-built for non-React stores; avoids tearing that a hand-rolled effect subscription allows. |
| Prefer a query library or framework loader for shared server data | Manual effect fetching reinvents caching, dedup, and invalidation that those already handle. |

## Memoization with a measured reason

| Practice | Detail |
|---|---|
| Add `useMemo`/`useCallback` only after profiling shows real cost | Each has overhead and obscures the code; preemptive memoization usually costs more than it saves. The React Compiler (19) auto-memoizes correct code, removing most manual need. |
| Wrap a component in `memo` only when it re-renders often with unchanged props | `memo` runs a prop comparison every render, wasted unless the child is genuinely expensive and its parent re-renders frequently with stable props. |
| Do not create objects or functions inline in props to a memoized child | A fresh `{}` or `() => {}` each render is a new reference that defeats `memo`. Hoist the constant or memoize it. |

## Server vs Client Components (RSC)

| Practice | Detail |
|---|---|
| Components are Server Components by default | There is no directive for them; they render ahead of time, can be `async`, and read databases or the filesystem directly. They cannot use `useState`, `useEffect`, event handlers, or browser APIs. |
| Mark interactivity with `"use client"` | The directive (top of file) makes a component and its imports run in the browser. Add it for anything using state, effects, refs to the DOM, or event handlers. |
| `"use server"` marks Server Functions, not Server Components | It tags `async` functions callable from the client that execute on the server, the opposite of what the name suggests. |
| The boundary flows one way and must be serializable | A Client Component cannot import a Server Component, but a Server Component can render one and pass it `children`. Props crossing the boundary must be serializable (no functions except Server Functions, no class instances). |
| Stream server data into a Client Component with `use()` | Start a promise on the server, pass it unawaited through `<Suspense>`, and unwrap it on the client with `use(promise)`. |
| RSC internals are not semver-stable in 19.x | The bundler/framework-facing APIs may break between 19.x minors; build on a framework that owns them rather than wiring RSC by hand. |

## React 19 features

| Feature | Detail |
|---|---|
| `ref` as a prop | Accept `ref` directly in props; `forwardRef` is deprecated for function components (still needed for class refs). A ref callback may now return a cleanup function. |
| Actions and `useActionState` | `const [state, action, isPending] = useActionState(async (prev, formData) => {...}, initial)`. Wires an async action into pending and error state; pass `action` to `<form action={...}>`, which auto-resets on success. |
| `useFormStatus` | `const { pending } = useFormStatus()` reads the enclosing `<form>`'s submission state from a design-system button without prop-drilling. Import from `react-dom`. |
| `useOptimistic` | `const [optimistic, setOptimistic] = useOptimistic(current)` shows a pending value immediately and reverts automatically when the action settles or fails. |
| `use()` | Reads a promise (suspends) or context, callable conditionally. It does not accept a promise created during render; create it in an event handler, a Server Component, or a cached source. |
| Document metadata | Render `<title>`, `<meta>`, and `<link>` anywhere; React hoists them to `<head>` and dedupes. Works client-side, in SSR, and in RSC, replacing most head-manager libraries. |
| Stylesheets and async scripts | `<link rel="stylesheet" precedence="...">` and `<script async>` may live in the tree; React orders, dedupes, and (for stylesheets) waits to load before revealing Suspense content. |
| `<Context>` as provider | Render `<ThemeContext value={...}>` directly; `<Context.Provider>` is deprecated. |

## Rendering, keys, refs, errors

| Practice | Detail |
|---|---|
| Give list items a stable unique key, never the array index | React matches elements across renders by key; an index remaps state to the wrong item on insert or reorder, while a stable id preserves identity and DOM. |
| Keep urgent updates responsive with `useTransition` / `useDeferredValue` | Mark heavy state work as a transition, or render an expensive view from a lagging copy, so typing and clicks commit first. `useDeferredValue(value, initial)` (19) supplies a first-render value. |
| Split routes and below-the-fold trees with `lazy()` and `<Suspense>` | Code-splitting at these boundaries shrinks the initial bundle so first paint does not pay for unreached screens. |
| Use `useRef` for non-render values, not displayed state | Refs hold mutable values for focusing, scrolling, measuring, animating, and timer ids. Mutating a ref does not re-render, so anything the UI shows must be state. |
| Expose a narrow imperative API with `useImperativeHandle` | Reveal specific methods, not the raw node, so callers cannot depend on internals. |
| Generate linked ids with `useId` | Stable, unique, SSR-safe ids for pairing labels with inputs, unlike ad-hoc counters that collide on hydration. |
| Prefer controlled inputs; choose uncontrolled deliberately | A controlled input drives value from state for validation and dynamic behavior; uncontrolled (`defaultValue` + ref) is fine for simple forms. Never flip an input between the two across renders. |
| Place Error Boundaries around independent sections | A boundary catches render errors in its subtree so one failed section degrades alone. It does not catch event-handler or async errors: those need `try/catch`. |

## Gotchas

- Reading state right after `setState` returns the old value; state updates are a snapshot for the next render, not a synchronous assignment.
- An index `key` looks fine until the list reorders or items are inserted, then component state attaches to the wrong row.
- An effect with a missing dependency does not "run less"; it runs with stale values and hides the bug.
- `use()` rejects a promise created during render; pass one created on the server, in a handler, or by a cache, or React warns.
- `"use server"` does not make a Server Component; it declares a Server Function. Server Components need no directive.
- A Client Component cannot import a Server Component; pass server output through `children` instead.
- Mutating an object already handed to JSX or to a hook is a Rules-of-React violation even though it may appear to work.
- A ref callback that uses an implicit arrow return (`ref={el => (x = el)}`) is now read as a cleanup function (19); use a block body.

## Sources

- [react.dev: You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect), [Rules of React](https://react.dev/reference/rules), [Rules of Hooks](https://react.dev/reference/rules/rules-of-hooks) - official docs; authoritative on purity, effect avoidance, and hook ordering.
- [React 19 release post](https://react.dev/blog/2024/12/05/react-19) - official; canonical list and signatures for Actions, `useActionState`, `useOptimistic`, `use()`, `ref` as prop, metadata, and `<Context>`.
- [react.dev: Server Components](https://react.dev/reference/rsc/server-components) and [Server Functions](https://react.dev/reference/rsc/server-functions) - official; the RSC boundary, directives, and serialization rules.
- [Dan Abramov: A Complete Guide to useEffect](https://overreacted.io/a-complete-guide-to-useeffect/) - former React core team; the closures-over-snapshots model and honest dependencies.
- [Kent C. Dodds: State Colocation will make your app faster](https://kentcdodds.com/blog/state-colocation-will-make-your-react-app-faster) - recognized React educator; the colocate-vs-lift decision framework.
- [react.dev: useMemo](https://react.dev/reference/react/useMemo) and [React Compiler](https://react.dev/learn/react-compiler) - official; when memoization earns its place and what the compiler now automates.
