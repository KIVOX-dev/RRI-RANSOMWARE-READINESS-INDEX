import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EmptyState } from "@/components/EmptyState";

describe("EmptyState", () => {
  it("renders the title and description", () => {
    render(<EmptyState title="Nothing here yet" description="Come back after you complete an assessment." />);
    expect(screen.getByText("Nothing here yet")).toBeInTheDocument();
    expect(screen.getByText("Come back after you complete an assessment.")).toBeInTheDocument();
  });
});
