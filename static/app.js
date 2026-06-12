(() => {
  const flowSources = [
    "https://cdn.jsdelivr.net/npm/react@18/umd/react.production.min.js",
    "https://cdn.jsdelivr.net/npm/react-dom@18/umd/react-dom.production.min.js",
    "https://cdn.jsdelivr.net/npm/reactflow@11.11.4/dist/umd/index.js",
  ];

  let flowLoadPromise = null;

  function onReady(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, { once: true });
    } else {
      callback();
    }
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      if (document.querySelector(`script[src="${src}"]`)) {
        resolve();
        return;
      }
      const script = document.createElement("script");
      script.src = src;
      script.async = true;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  function loadStylesheet(href) {
    if (document.querySelector(`link[href="${href}"]`)) {
      return;
    }
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = href;
    document.head.appendChild(link);
  }

  function ensureReactFlow() {
    if (flowLoadPromise) {
      return flowLoadPromise;
    }
    loadStylesheet("https://cdn.jsdelivr.net/npm/reactflow@11.11.4/dist/style.css");
    flowLoadPromise = flowSources.reduce((promise, src) => {
      return promise.then(() => loadScript(src));
    }, Promise.resolve());
    return flowLoadPromise;
  }

  window.tteBeginJourney = function tteBeginJourney() {
    const status = document.querySelector("#journey-status");
    if (status) {
      status.classList.add("is-active");
    }
    document.querySelectorAll(".mind-reveal").forEach((node) => {
      node.style.opacity = "0.22";
      node.style.filter = "blur(10px)";
    });
  };

  function endJourney() {
    const status = document.querySelector("#journey-status");
    if (status) {
      status.classList.remove("is-active");
    }
  }

  function wireAnalyzeButton(root = document) {
    root.querySelectorAll(".analyze-button").forEach((buttonShell) => {
      if (buttonShell.dataset.tteWired === "true") {
        return;
      }
      buttonShell.dataset.tteWired = "true";
      buttonShell.addEventListener(
        "click",
        () => {
          window.tteBeginJourney();
        },
        { capture: true }
      );
    });
  }

  function wirePlanets(root = document) {
    root.querySelectorAll(".perspective-orbit").forEach((orbit) => {
      if (orbit.dataset.tteWired === "true") {
        return;
      }
      orbit.dataset.tteWired = "true";
      orbit.querySelectorAll(".planet").forEach((planet) => {
        planet.addEventListener("click", () => {
          const key = planet.dataset.perspective;
          orbit.querySelectorAll(".planet").forEach((item) => item.classList.remove("active"));
          orbit.querySelectorAll(".perspective-panel").forEach((panel) => panel.classList.remove("active"));
          planet.classList.add("active");
          const panel = orbit.querySelector(`[data-perspective-panel="${key}"]`);
          if (panel) {
            panel.classList.add("active");
          }
        });
      });
    });
  }

  function wireEmotionBubbles(root = document) {
    root.querySelectorAll(".emotion-bubble").forEach((bubble) => {
      if (bubble.dataset.tteWired === "true") {
        return;
      }
      bubble.dataset.tteWired = "true";
      bubble.addEventListener("click", () => {
        bubble.classList.toggle("is-open");
      });
    });
  }

  function wireMisunderstandingCards(root = document) {
    root.querySelectorAll(".misread-card").forEach((card) => {
      if (card.dataset.tteMisunderstood === "true") {
        return;
      }
      card.dataset.tteMisunderstood = "true";
      card.addEventListener("click", (event) => {
        event.preventDefault();
        card.classList.toggle("is-open");
        card.style.animation = "revealMind 420ms ease both";
      });
    });
  }

  function wireFutureEchoes(root = document) {
    root.querySelectorAll(".future-card").forEach((card) => {
      if (card.dataset.tteFuture === "true") {
        return;
      }
      card.dataset.tteFuture = "true";
      const cards = card.parentElement?.querySelectorAll(".future-card");
      card.addEventListener("click", (event) => {
        event.preventDefault();
        if (cards) {
          cards.forEach((c) => c.classList.remove("active"));
        }
        card.classList.add("active");
        card.style.animation = "revealMind 420ms ease both";
        const timeline = card.querySelector(".future-timeline");
        if (timeline) {
          timeline.style.animation = "timelineReveal 480ms ease 100ms both";
        }
      });
    });
  }

  function buildFlowElements(graph) {
    const nodes = graph.nodes.map((node) => ({
      id: node.id,
      type: "default",
      position: { x: node.x, y: node.y },
      data: {
        label: window.React.createElement(
          "div",
          { className: `tte-flow-node ${node.kind}` },
          node.label
        ),
        raw: node,
      },
      draggable: true,
    }));

    const edges = graph.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      animated: true,
      style: { stroke: "rgba(125, 211, 252, 0.62)", strokeWidth: 1.5 },
    }));

    return { nodes, edges };
  }

  function updateUniversePanel(shell, node) {
    const panel = shell.querySelector(".universe-panel");
    if (!panel || !node) {
      return;
    }
    const category = node.category || node.kind || "Node";
    const label = node.label || "Selected node";
    const description = node.description || "This point belongs to the emotional constellation.";
    panel.innerHTML = `
      <span class="node-label">${escapeHtml(category)}</span>
      <strong>${escapeHtml(label)}</strong>
      <p>${escapeHtml(description)}</p>
    `;
    panel.classList.add("is-active");
  }

  function renderReactFlow(shell, graph) {
    const mount = shell.querySelector(".react-flow-mount");
    if (!mount || mount.dataset.tteRendered === "true") {
      return;
    }
    mount.dataset.tteRendered = "true";

    ensureReactFlow()
      .then(() => {
        const React = window.React;
        const ReactDOM = window.ReactDOM;
        const ReactFlowPackage = window.ReactFlow || window.ReactFlowRenderer;
        if (!React || !ReactDOM || !ReactFlowPackage) {
          throw new Error("React Flow globals unavailable");
        }

        const ReactFlow = ReactFlowPackage.default || ReactFlowPackage.ReactFlow || ReactFlowPackage;
        const Background = ReactFlowPackage.Background;
        const Controls = ReactFlowPackage.Controls;
        const MiniMap = ReactFlowPackage.MiniMap;
        const elements = buildFlowElements(graph);

        function EmotionalMap() {
          return React.createElement(
            ReactFlow,
            {
              nodes: elements.nodes,
              edges: elements.edges,
              fitView: true,
              nodesDraggable: true,
              panOnScroll: true,
              zoomOnScroll: true,
              onNodeClick: (_event, node) => updateUniversePanel(shell, node.data.raw),
              proOptions: { hideAttribution: true },
            },
            Background ? React.createElement(Background, { color: "rgba(125, 211, 252, 0.18)", gap: 32 }) : null,
            Controls ? React.createElement(Controls, { showInteractive: false }) : null,
            MiniMap ? React.createElement(MiniMap, { pannable: true, zoomable: true }) : null
          );
        }

        ReactDOM.createRoot(mount).render(React.createElement(EmotionalMap));
        const fallback = shell.querySelector(".graph-fallback");
        if (fallback) {
          fallback.innerHTML = "";
        }
      })
      .catch(() => {
        renderGraphFallback(shell, graph);
      });
  }

  function renderGraphFallback(shell, graph) {
    const fallback = shell.querySelector(".graph-fallback");
    if (!fallback || fallback.dataset.tteRendered === "true") {
      return;
    }
    fallback.dataset.tteRendered = "true";

    const width = 1000;
    const height = 620;
    const positions = new Map(
      graph.nodes.map((node) => [
        node.id,
        {
          x: Math.min(width - 120, Math.max(120, node.x + width / 2)),
          y: Math.min(height - 80, Math.max(80, node.y + height / 2)),
        },
      ])
    );

    const edgeMarkup = graph.edges
      .map((edge) => {
        const source = positions.get(edge.source);
        const target = positions.get(edge.target);
        if (!source || !target) {
          return "";
        }
        return `<line data-source="${edge.source}" data-target="${edge.target}" x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" />`;
      })
      .join("");

    const nodeMarkup = graph.nodes
      .map((node) => {
        const point = positions.get(node.id);
        if (!point) {
          return "";
        }
        const radius = node.kind === "conflict" ? 70 : 48;
        const label = escapeHtml(String(node.label));
        return `
          <g class="fallback-node ${node.kind}" data-node-id="${node.id}">
            <circle cx="${point.x}" cy="${point.y}" r="${radius}"></circle>
            <text x="${point.x}" y="${point.y}" text-anchor="middle" dominant-baseline="middle">${label}</text>
          </g>
        `;
      })
      .join("");

    fallback.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Emotional universe graph">
        <defs>
          <filter id="tte-glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"></feGaussianBlur>
            <feMerge>
              <feMergeNode in="coloredBlur"></feMergeNode>
              <feMergeNode in="SourceGraphic"></feMergeNode>
            </feMerge>
          </filter>
        </defs>
        <g class="fallback-edges">${edgeMarkup}</g>
        <g class="fallback-nodes">${nodeMarkup}</g>
      </svg>
    `;
    wireFallbackGraph(shell, fallback, positions, graph);
  }

  function wireFallbackGraph(shell, fallback, positions, graph) {
    const svg = fallback.querySelector("svg");
    if (!svg) {
      return;
    }

    let viewBox = { x: 0, y: 0, width: 1000, height: 620 };
    let activeNode = null;
    let panStart = null;

    function setViewBox() {
      svg.setAttribute("viewBox", `${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`);
    }

    function svgPoint(event) {
      const point = svg.createSVGPoint();
      point.x = event.clientX;
      point.y = event.clientY;
      return point.matrixTransform(svg.getScreenCTM().inverse());
    }

    function updateNode(nodeId, point) {
      positions.set(nodeId, { x: point.x, y: point.y });
      const group = svg.querySelector(`[data-node-id="${nodeId}"]`);
      if (group) {
        const circle = group.querySelector("circle");
        const text = group.querySelector("text");
        if (circle) {
          circle.setAttribute("cx", point.x);
          circle.setAttribute("cy", point.y);
        }
        if (text) {
          text.setAttribute("x", point.x);
          text.setAttribute("y", point.y);
        }
      }
      svg.querySelectorAll(`line[data-source="${nodeId}"]`).forEach((line) => {
        line.setAttribute("x1", point.x);
        line.setAttribute("y1", point.y);
      });
      svg.querySelectorAll(`line[data-target="${nodeId}"]`).forEach((line) => {
        line.setAttribute("x2", point.x);
        line.setAttribute("y2", point.y);
      });
    }

    svg.addEventListener("pointerdown", (event) => {
      const node = event.target.closest(".fallback-node");
      if (node) {
        activeNode = node.dataset.nodeId;
        const graphNode = graph.nodes.find((item) => item.id === activeNode);
        updateUniversePanel(shell, graphNode);
        svg.setPointerCapture(event.pointerId);
        return;
      }
      panStart = { point: svgPoint(event), viewBox: { ...viewBox } };
      svg.setPointerCapture(event.pointerId);
    });

    svg.addEventListener("pointermove", (event) => {
      if (activeNode) {
        updateNode(activeNode, svgPoint(event));
        return;
      }
      if (panStart) {
        const point = svgPoint(event);
        viewBox.x = panStart.viewBox.x - (point.x - panStart.point.x);
        viewBox.y = panStart.viewBox.y - (point.y - panStart.point.y);
        setViewBox();
      }
    });

    svg.addEventListener("pointerup", () => {
      activeNode = null;
      panStart = null;
    });

    svg.addEventListener(
      "wheel",
      (event) => {
        event.preventDefault();
        const point = svgPoint(event);
        const scale = event.deltaY > 0 ? 1.08 : 0.92;
        const nextWidth = Math.min(1800, Math.max(360, viewBox.width * scale));
        const nextHeight = Math.min(1120, Math.max(240, viewBox.height * scale));
        viewBox.x = point.x - ((point.x - viewBox.x) / viewBox.width) * nextWidth;
        viewBox.y = point.y - ((point.y - viewBox.y) / viewBox.height) * nextHeight;
        viewBox.width = nextWidth;
        viewBox.height = nextHeight;
        setViewBox();
      },
      { passive: false }
    );
  }

  function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value;
    return div.innerHTML;
  }

  function renderUniverses(root = document) {
    root.querySelectorAll(".universe-shell").forEach((shell) => {
      if (shell.dataset.tteUniverse === "rendering") {
        return;
      }
      const rawGraph = shell.dataset.tteGraph;
      if (!rawGraph) {
        return;
      }
      shell.dataset.tteUniverse = "rendering";
      try {
        const graph = JSON.parse(rawGraph);
        renderReactFlow(shell, graph);
      } catch {
        shell.dataset.tteUniverse = "error";
      }
    });
  }

  function enhance(root = document) {
    wireAnalyzeButton(root);
    wirePlanets(root);
    wireEmotionBubbles(root);
    wireMisunderstandingCards(root);
    wireFutureEchoes(root);
    renderUniverses(root);
  }

  function nodeContainsResult(node) {
    if (!(node instanceof Element)) {
      return false;
    }
    return Boolean(
      node.matches(".mind-reveal") ||
        node.querySelector(".mind-reveal") ||
        node.matches(".error-card") ||
        node.querySelector(".error-card")
    );
  }

  onReady(() => {
    enhance();
    const observer = new MutationObserver((mutations) => {
      const shouldEnhance = mutations.some((mutation) => mutation.addedNodes.length > 0);
      if (shouldEnhance) {
        const hasResult = mutations.some((mutation) => {
          return Array.from(mutation.addedNodes).some(nodeContainsResult);
        });
        window.requestAnimationFrame(() => {
          enhance();
          if (hasResult) {
            endJourney();
          }
        });
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  });
})();
