import { useEffect, useRef, useCallback, useState } from "react";
import { subscribeDisputeSSE } from "../lib/api";

export function useDisputeSSE(disputeId, onUpdate, onError) {
  const cleanupRef = useRef(null);
  const [connected, setConnected] = useState(false);

  const unsubscribe = useCallback(() => {
    cleanupRef.current?.();
    cleanupRef.current = null;
    setConnected(false);
  }, []);

  useEffect(() => {
    if (!disputeId) return;

    const wrappedError = (err) => {
      setConnected(false);
      onError?.(err);
    };

    const wrappedUpdate = (data) => {
      setConnected(true);
      onUpdate(data);
    };

    cleanupRef.current = subscribeDisputeSSE(disputeId, wrappedUpdate, wrappedError);

    return unsubscribe;
  }, [disputeId, onUpdate, onError, unsubscribe]);

  return { unsubscribe, connected };
}
