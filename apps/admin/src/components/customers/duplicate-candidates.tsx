import Link from "next/link";

import type { DuplicateDetectionResult } from "@/lib/api/customer-types";

export function DuplicateCandidates({
  candidates,
}: {
  candidates: DuplicateDetectionResult[];
}) {
  if (candidates.length === 0) {
    return null;
  }

  return (
    <div className="candidate-list">
      {candidates.map((candidate) => (
        <article className="candidate-item" key={candidate.customer_id}>
          <div className="candidate-heading">
            <div>
              <strong>{candidate.display_name}</strong>
              <span>{candidate.reasons.join(", ")}</span>
            </div>
            <span className={`confidence confidence-${candidate.confidence}`}>
              {candidate.confidence}
            </span>
          </div>
          <div className="candidate-footer">
            <span>Score: {candidate.score}</span>
            <Link href={`/customers/${candidate.customer_id}`}>Ver cliente</Link>
          </div>
        </article>
      ))}
    </div>
  );
}
