import Mathlib.Tactic

/-!
# <KEY> — equations transcribed from <citation>, DOI <doi>

Verification levels used in this file
* (D) Dimensional homogeneity: every additive term and both sides of each equation carry the same
      SI dimension (exponents of kg, m, s, K, mol), proved by `decide`.
* (A) Algebra: rearrangements or relations the paper derives between its equations, proved over ℝ.
* (N) Numerics: values the paper computes from its equations, re-computed with `norm_num`
      (rounding to the paper's reported precision is stated explicitly).
* (F) Formalisation: each algebraic equation is written as a Lean definition over ℝ and type-checks.
-/

namespace PaperKEY

/-- SI dimension as integer exponents of kg, m, s, K, mol. -/
structure Dim where
  M : Int
  L : Int
  T : Int
  Θ : Int
  N : Int
  deriving DecidableEq, Repr

namespace Dim
def mul (a b : Dim) : Dim := ⟨a.M + b.M, a.L + b.L, a.T + b.T, a.Θ + b.Θ, a.N + b.N⟩
def div (a b : Dim) : Dim := ⟨a.M - b.M, a.L - b.L, a.T - b.T, a.Θ - b.Θ, a.N - b.N⟩
def npow (a : Dim) (n : Int) : Dim := ⟨a.M * n, a.L * n, a.T * n, a.Θ * n, a.N * n⟩
instance : Mul Dim := ⟨mul⟩
instance : Div Dim := ⟨div⟩
def one : Dim := ⟨0, 0, 0, 0, 0⟩      -- dimensionless
def kg : Dim := ⟨1, 0, 0, 0, 0⟩
def m : Dim := ⟨0, 1, 0, 0, 0⟩
def s : Dim := ⟨0, 0, 1, 0, 0⟩
def K : Dim := ⟨0, 0, 0, 1, 0⟩
def mol : Dim := ⟨0, 0, 0, 0, 1⟩
def m2 : Dim := m * m
def m3 : Dim := m * m * m
def J : Dim := kg * m2 / (s * s)        -- energy
def W : Dim := J / s                     -- power
def Pa : Dim := kg / (m * s * s)         -- pressure
def N_ : Dim := kg * m / (s * s)         -- force
end Dim

open Dim

-- Example (D): Fourier's law q'' = -k dT/dx : W m⁻² = (W m⁻¹ K⁻¹)(K m⁻¹)
theorem example_fourier_dims : W / m2 = (W / (m * K)) * (K / m) := by decide

-- Example (F)+(A): a definition and an algebraic rearrangement
noncomputable def fourier (k dTdx : ℝ) : ℝ := -k * dTdx
theorem example_rearrange (k dTdx q : ℝ) (hk : k ≠ 0) (h : q = fourier k dTdx) : dTdx = -q / k := by
  unfold fourier at h; field_simp; linarith

-- Example (N): a value reported to one decimal place
def rounds1 (x y : ℚ) : Prop := y - 1/20 ≤ x ∧ x < y + 1/20
theorem example_numeric : rounds1 ((3600 * 3 / 10 * 1 / 2 : ℚ) / 1) 540 := by norm_num [rounds1]

end PaperKEY
