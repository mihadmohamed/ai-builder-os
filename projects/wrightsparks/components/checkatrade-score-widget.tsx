"use client";

import { useEffect, useRef, useState } from "react";

type CheckatradeScoreWidgetProps = {
  companyId: string;
};

export function CheckatradeScoreWidget({ companyId }: CheckatradeScoreWidgetProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [widgetReady, setWidgetReady] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.innerHTML = "";
    setWidgetReady(false);

    const script = document.createElement("script");
    script.src = "https://www.checkatrade.com/static/js/reviews-score-widget.js";
    script.async = true;
    script.setAttribute("data-company-id", companyId);

    const readyTimer = window.setTimeout(() => {
      if ((container.textContent || "").trim().length > 0 || container.children.length > 1) {
        setWidgetReady(true);
      }
    }, 1200);

    script.addEventListener("load", () => {
      window.setTimeout(() => {
        if ((container.textContent || "").trim().length > 0 || container.children.length > 1) {
          setWidgetReady(true);
        }
      }, 200);
    });

    container.appendChild(script);

    return () => {
      window.clearTimeout(readyTimer);
      container.innerHTML = "";
    };
  }, [companyId]);

  return (
    <div className="checkatrade-widget-shell">
      <div
        ref={containerRef}
        className={`checkatrade-widget-host${widgetReady ? " is-ready" : ""}`}
        aria-label="Checkatrade rating widget"
      />
      {!widgetReady ? (
        <div className="checkatrade-widget-fallback" aria-hidden="true">
          <p>
            ★★★★★ <strong>10/10</strong>
            <span>Checkatrade</span>
          </p>
          <p>
            ★★★★★ <strong>5.0</strong>
            <span>Google</span>
          </p>
        </div>
      ) : null}
    </div>
  );
}
