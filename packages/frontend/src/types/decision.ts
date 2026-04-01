export interface DecisionNode {
  id: string
  decision_external_id: string
  decision_type: string
  sequence_number: number
  parent_decision_id: string | null
  action_type: string | null
  duration_ms: number | null
  has_error: boolean
  policy_summary: Record<string, unknown> | null
  input_context: Record<string, unknown> | null
  reasoning_trace: string | null
  action_detail: Record<string, unknown> | null
  output: Record<string, unknown> | null
  side_effects: Record<string, unknown> | null
  created_at: string
}

export interface DecisionTreeNode extends Omit<DecisionNode, 'side_effects'> {
  children: DecisionTreeNode[]
}

export interface DecisionTreeResponse {
  session_id: string
  roots: DecisionTreeNode[]
}
