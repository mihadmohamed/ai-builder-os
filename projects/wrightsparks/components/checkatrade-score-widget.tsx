"use client";

import { useEffect, useRef, useState } from "react";

declare global {
  interface Window {
    _checkatradeConfig?: {
      uniqueName: string;
      theme: "blue" | "red" | "white";
      companyId: string;
    };
  }
}

type CheckatradeReviewWidgetProps = {
  companyId: string;
  uniqueName: string;
  theme?: "blue" | "red" | "white";
};

function hostHasRenderedWidget(host: HTMLDivElement) {
  return host.querySelector("#chktrade_widget") !== null || host.children.length > 1;
}

export function CheckatradeReviewWidget({
  companyId,
  uniqueName,
  theme = "white",
}: CheckatradeReviewWidgetProps) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const [widgetReady, setWidgetReady] = useState(false);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    host.innerHTML = "";
    setWidgetReady(false);

    const previousConfig = window._checkatradeConfig;
    window._checkatradeConfig = { companyId, uniqueName, theme };

    const script = document.createElement("script");
    script.src = "https://www.checkatrade.com/static/js/widget.js";
    script.async = true;

    const markReadyIfPresent = () => {
      if (hostHasRenderedWidget(host)) {
        setWidgetReady(true);
      }
    };

    const timeoutId = window.setTimeout(markReadyIfPresent, 1200);
    script.addEventListener("load", () => {
      window.setTimeout(markReadyIfPresent, 250);
    });
    script.addEventListener("error", () => {
      setWidgetReady(false);
    });

    host.appendChild(script);

    return () => {
      window.clearTimeout(timeoutId);
      host.innerHTML = "";
      if (previousConfig) {
        window._checkatradeConfig = previousConfig;
      } else {
        delete window._checkatradeConfig;
      }
    };
  }, [companyId, uniqueName, theme]);

  return (
    <div className="checkatrade-review-button-shell">
      <div
        ref={hostRef}
        className={`checkatrade-review-button-host${widgetReady ? " is-ready" : ""}`}
        aria-label="Checkatrade review button"
        hidden={!widgetReady}
      />
      {!widgetReady ? (
        <a
          className="button dark"
          href="https://www.checkatrade.com/trades/wrightsparks991862/reviews"
          target="_blank"
          rel="noreferrer"
        >
          View on Checkatrade ↗
        </a>
      ) : null}
    </div>
  );
}
