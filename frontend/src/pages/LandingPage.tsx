import { Link } from 'react-router-dom'
import { motion, useReducedMotion } from 'motion/react'
import {
  Shield,
  ArrowRight,
  Upload,
  Database,
  Tag,
  ArrowUpDown,
  AlertTriangle,
  Search,
  Bot,
  ChevronRight,
  FileText,
  Lock,
  Users,
  CheckCircle2,
} from 'lucide-react'
import LiquidEther from '../components/landing/LiquidEther'
import { ScrollStack, ScrollStackItem } from '../components/landing/ScrollStack'
import { HeroDashboardMock } from '../components/landing/HeroDashboardMock'
import { BentoGrid, BentoCard } from '../components/landing/MagicBento'

// ─── Animated word-by-word headline ─────────────────────────────────────────

function AnimatedHeadline({ text, className }: { text: string; className?: string }) {
  const prefersReduced = useReducedMotion()
  const words = text.split(' ')

  return (
    <span className={className}>
      {words.map((word, i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0, y: prefersReduced ? 0 : 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: prefersReduced ? 0.15 : 0.5,
            delay: prefersReduced ? 0 : i * 0.065,
            ease: [0.16, 1, 0.3, 1],
          }}
          className="inline-block"
        >
          {word}&nbsp;
        </motion.span>
      ))}
    </span>
  )
}

// ─── Navigation anchors ──────────────────────────────────────────────────────

const NAV_ANCHORS = [
  { label: 'Product', id: 'product' },
  { label: 'Workflow', id: 'workflow' },
  { label: 'Evidence', id: 'evidence' },
  { label: 'Security', id: 'security' },
]

// ─── Workflow cards for ScrollStack ─────────────────────────────────────────

const WORKFLOW_CARDS = [
  {
    number: '01',
    title: 'Ingest & Extract',
    desc: 'Upload PDFs, CSVs, and spreadsheets. AuditPilot parses vendor ledgers, TDS workings, Form 26AS statements, challans, and invoices into structured records — automatically, with no manual effort.',
    icons: [Upload, Database],
    accent: 'from-blue-500/20 to-blue-600/5',
    iconColor: 'text-blue-400',
    borderColor: 'border-blue-500/20',
  },
  {
    number: '02',
    title: 'Classify & Normalize',
    desc: 'Automatically classify documents by type — ledger, challan, working sheet, or invoice. Normalize extracted records across all sources to enable reliable, deterministic cross-matching.',
    icons: [Tag, ArrowUpDown],
    accent: 'from-violet-500/20 to-violet-600/5',
    iconColor: 'text-violet-400',
    borderColor: 'border-violet-500/20',
  },
  {
    number: '03',
    title: 'Detect Risks',
    desc: 'Run configurable, rule-based risk checks: TDS rate mismatches, short deposit, missing PAN compliance, duplicate invoices, and more. Transparent logic. No black-box decisions.',
    icons: [AlertTriangle],
    accent: 'from-amber-500/20 to-amber-600/5',
    iconColor: 'text-amber-400',
    borderColor: 'border-amber-500/20',
  },
  {
    number: '04',
    title: 'Investigate with Evidence',
    desc: 'Every risk finding links to indexed source records with full citations. Query the AI agent in plain language — it explains findings using retrieved evidence and never invents them.',
    icons: [Search, Bot],
    accent: 'from-teal-500/20 to-teal-600/5',
    iconColor: 'text-teal-400',
    borderColor: 'border-teal-500/20',
  },
]

// ─── Security / evidence points ───────────────────────────────────────────────

const SECURITY_POINTS = [
  {
    icon: Lock,
    title: 'Workspace-Scoped Access',
    desc: 'All data is isolated within a workspace. No cross-client data exposure.',
  },
  {
    icon: FileText,
    title: 'Source Trace & Citations',
    desc: 'Every risk finding links to the precise source record and originating document.',
  },
  {
    icon: Users,
    title: 'Role-Based Permissions',
    desc: 'Owner, admin, editor, and viewer roles define exactly what each user can access and do.',
  },
  {
    icon: CheckCircle2,
    title: 'Auditable Rule Logic',
    desc: 'Risk rules are transparent and configurable. Every finding is explainable and traceable.',
  },
]

// ─── Landing Page ─────────────────────────────────────────────────────────────

export function LandingPage() {
  const prefersReduced = useReducedMotion()

  const fadeUp = (delay = 0) => ({
    initial: { opacity: 0, y: prefersReduced ? 0 : 12 },
    animate: { opacity: 1, y: 0 },
    transition: {
      duration: 0.4,
      delay: prefersReduced ? 0 : delay,
      ease: [0.16, 1, 0.3, 1] as [number, number, number, number],
    },
  })

  const fadeUpInView = (delay = 0) => ({
    initial: { opacity: 0, y: prefersReduced ? 0 : 12 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true, margin: '-60px' } as const,
    transition: {
      duration: 0.4,
      delay: prefersReduced ? 0 : delay,
      ease: [0.16, 1, 0.3, 1] as [number, number, number, number],
    },
  })

  return (
    <div className="min-h-screen bg-[#0B1629] text-white">

      {/* ═══ FIXED HEADER ════════════════════════════════════════════════════ */}
      <header className="fixed top-0 left-0 right-0 z-40 bg-[#0B1629]/80 backdrop-blur-md border-b border-white/[0.04]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
          {/* Brand */}
          <Link
            to="/"
            className="flex items-center gap-2.5 flex-shrink-0 rounded-lg focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400"
          >
            <img src="/app-icon.png" alt="AuditPilot" className="w-7 h-7 rounded-lg object-contain flex-shrink-0" />
            <span className="text-[15px] font-bold text-white tracking-tight">AuditPilot</span>
          </Link>

          {/* Nav anchors (desktop) */}
          <nav className="hidden md:flex items-center gap-1" aria-label="Main navigation">
            {NAV_ANCHORS.map(({ label, id }) => (
              <a
                key={id}
                href={`#${id}`}
                onClick={(e) => {
                  e.preventDefault()
                  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
                }}
                className="px-3 py-2 text-sm font-medium text-slate-400 hover:text-slate-100 rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400"
              >
                {label}
              </a>
            ))}
          </nav>

          {/* Primary CTA */}
          <Link
            to="/login"
            className="group flex-shrink-0 flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0B1629]"
          >
            Request Access
            <ArrowRight className="w-3.5 h-3.5 transition-transform duration-200 group-hover:translate-x-1" />
          </Link>
        </div>
      </header>

      {/* ═══ HERO ══════════════════════════════════════════════════════════════ */}
      <section
        id="product"
        className="relative min-h-screen flex items-center overflow-hidden"
        aria-labelledby="hero-heading"
      >
        {/* LiquidEther background */}
        <div className="absolute inset-0 z-0">
          <LiquidEther
            colors={['#2563EB', '#7C3AED', '#14B8A6']}
            mouseForce={20}
            cursorSize={120}
            isViscous={false}
            viscous={30}
            iterationsViscous={32}
            iterationsPoisson={32}
            resolution={0.5}
            isBounce={false}
            autoDemo
            autoSpeed={0.4}
            autoIntensity={2.0}
            takeoverDuration={0.25}
            autoResumeDelay={2000}
            autoRampDuration={0.8}
          />
        </div>

        {/* Dark overlay for text readability */}
        <div
          className="absolute inset-0 z-[1]"
          style={{
            background:
              'radial-gradient(ellipse at 30% 50%, rgba(11,22,41,0.4) 0%, rgba(11,22,41,0.7) 100%)',
          }}
          aria-hidden="true"
        />

        {/* Hero content */}
        <div className="relative z-[2] max-w-7xl mx-auto px-4 sm:px-6 pt-28 pb-32 w-full">
          {/* Badge */}
          <motion.div
            {...fadeUp(0)}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-blue-400/20 bg-blue-500/10 text-xs font-medium text-blue-300 mb-8 backdrop-blur-sm"
          >
            <Shield className="w-3.5 h-3.5 flex-shrink-0" />
            AI-Powered Audit Intelligence
          </motion.div>

          {/* Headline */}
          <h1
            id="hero-heading"
            className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-extrabold leading-[1.08] tracking-tight text-white mb-6 max-w-4xl"
          >
            <AnimatedHeadline text="Evidence-backed audit intelligence" />
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-violet-400 to-teal-400 bg-clip-text text-transparent">
              <AnimatedHeadline text="for audit and compliance teams" />
            </span>
          </h1>

          {/* Subtitle */}
          <motion.p
            {...fadeUp(0.55)}
            className="text-base sm:text-lg text-slate-400 leading-relaxed mb-10 max-w-2xl"
          >
            Ingest audit and tax documentation at scale. Extract, normalize, and detect risks
            deterministically. Investigate findings through a source-traceable AI agent grounded
            in your evidence — not assumptions.
          </motion.p>

          {/* CTAs */}
          <motion.div {...fadeUp(0.7)} className="flex flex-wrap gap-4">
            <Link
              to="/login"
              className="group inline-flex items-center gap-2 px-7 py-3.5 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-all shadow-lg shadow-blue-600/25 hover:shadow-blue-600/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0B1629]"
            >
              Request Access
              <ArrowRight className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1" />
            </Link>
            <a
              href="#workflow"
              onClick={(e) => {
                e.preventDefault()
                document.getElementById('workflow')?.scrollIntoView({ behavior: 'smooth' })
              }}
              className="group inline-flex items-center gap-2 px-7 py-3.5 text-sm font-semibold text-slate-300 border border-white/10 hover:border-white/20 hover:text-white bg-white/5 hover:bg-white/10 backdrop-blur-sm rounded-xl transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0B1629]"
            >
              Explore Workflow
              <ChevronRight className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1" />
            </a>
          </motion.div>
        </div>

        {/* Gradient fade into next section — scrolls with the page */}
        <div
          className="absolute bottom-0 left-0 right-0 h-48 z-[1] pointer-events-none"
          style={{
            background: 'linear-gradient(to bottom, transparent 0%, #0B1629 100%)',
          }}
        />
      </section>

      {/* ═══ PRODUCT PREVIEW ══════════════════════════════════════════════ */}
      <section className="relative py-16 sm:py-24" aria-label="Product preview">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <motion.div {...fadeUpInView(0)} className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
              See the{' '}
              <span className="bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">
                platform in action
              </span>
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto text-sm sm:text-base leading-relaxed">
              A unified workspace for document ingestion, risk findings, evidence retrieval, and
              AI-assisted investigation — purpose-built for audit professionals.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: prefersReduced ? 0 : 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-60px' }}
            transition={{
              duration: 0.6,
              delay: prefersReduced ? 0 : 0.15,
              ease: [0.16, 1, 0.3, 1],
            }}
          >
            <HeroDashboardMock />
          </motion.div>
        </div>
      </section>

      {/* ═══ WORKFLOW — SCROLL STACK ════════════════════════════════════════ */}
      <section id="workflow" className="relative py-12 sm:py-16" aria-labelledby="workflow-heading">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <motion.div {...fadeUpInView(0)} className="text-center mb-16">
            <h2
              id="workflow-heading"
              className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-4"
            >
              From document ingestion to{' '}
              <span className="bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">
                audit intelligence
              </span>
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto text-sm sm:text-base leading-relaxed">
              A deterministic pipeline handles every stage. The AI agent explains findings grounded
              in retrieved evidence — it is never the source of truth for risk detection.
            </p>
          </motion.div>

          <ScrollStack scrollBudgetVh={100} stackOffset={36}>
            {WORKFLOW_CARDS.map((card) => (
              <ScrollStackItem key={card.number}>
                <div
                  className={`relative rounded-2xl border ${card.borderColor} bg-gradient-to-br ${card.accent} backdrop-blur-sm overflow-hidden`}
                  style={{
                    background: `linear-gradient(135deg, rgba(15,23,42,0.9) 0%, rgba(15,23,42,0.95) 100%)`,
                    borderColor: undefined,
                  }}
                >
                  {/* Subtle accent glow */}
                  <div
                    className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r ${card.accent} opacity-60`}
                  />

                  <div className="p-6 sm:p-8">
                    <div className="flex items-start gap-5">
                      {/* Number */}
                      <span className="text-3xl sm:text-4xl font-bold text-white/10 tabular-nums leading-none flex-shrink-0">
                        {card.number}
                      </span>

                      <div className="flex-1 min-w-0">
                        {/* Icons + Title */}
                        <div className="flex items-center gap-3 mb-3">
                          {card.icons.map((Icon, j) => (
                            <div
                              key={j}
                              className={`w-9 h-9 rounded-lg flex items-center justify-center ${card.iconColor} bg-white/5`}
                            >
                              <Icon className="w-[18px] h-[18px]" />
                            </div>
                          ))}
                          <h3 className="text-lg sm:text-xl font-semibold text-white">
                            {card.title}
                          </h3>
                        </div>

                        {/* Description */}
                        <p className="text-sm text-slate-400 leading-relaxed">{card.desc}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </ScrollStackItem>
            ))}
          </ScrollStack>
        </div>
      </section>

      {/* ═══ FEATURES — BENTO GRID ═══════════════════════════════════════════ */}
      <section
        id="features"
        className="relative py-16 sm:py-24 border-t border-white/[0.04]"
        aria-labelledby="features-heading"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <motion.div {...fadeUpInView(0)} className="text-center mb-14">
            <h2
              id="features-heading"
              className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-4"
            >
              Built for audit and compliance professionals
            </h2>
            <p className="text-slate-400 max-w-lg mx-auto text-sm sm:text-base leading-relaxed">
              Every capability maps directly to a stage of the audit review process — from document
              intake to evidence-backed findings.
            </p>
          </motion.div>

          <BentoGrid>
            {/* Row 1: hero card spans 2 cols */}
            <BentoCard
              colSpan={2}
              glowColor="37, 99, 235"
              className="min-h-[200px]"
            >
              <div className="p-6 sm:p-8 h-full flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-blue-500/10">
                      <Database className="w-5 h-5 text-blue-400" />
                    </div>
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-teal-500/10">
                      <Tag className="w-5 h-5 text-teal-400" />
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">Intelligent Document Processing</h3>
                  <p className="text-sm text-slate-400 leading-relaxed max-w-lg">
                    Ingest audit and tax documentation at scale. AuditPilot parses vendor ledgers,
                    TDS workings, Form 26AS statements, challans, and invoices into structured records
                    with zero manual effort.
                  </p>
                </div>
                <div className="flex gap-2 mt-5">
                  <span className="text-[10px] px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-300 font-medium">PDF</span>
                  <span className="text-[10px] px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-300 font-medium">CSV</span>
                  <span className="text-[10px] px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-300 font-medium">XLSX</span>
                  <span className="text-[10px] px-2.5 py-1 rounded-full bg-teal-500/10 text-teal-300 font-medium">Auto-classify</span>
                </div>
              </div>
            </BentoCard>

            <BentoCard glowColor="245, 158, 11" className="min-h-[200px]">
              <div className="p-6 sm:p-8 h-full flex flex-col">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-amber-500/10 mb-4">
                  <ArrowUpDown className="w-5 h-5 text-amber-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Cross-Source Record Normalization</h3>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Standardize extracted records across all document sources, enabling reliable
                  deterministic cross-matching and comparison at scale.
                </p>
              </div>
            </BentoCard>

            {/* Row 2 */}
            <BentoCard glowColor="239, 68, 68" className="min-h-[200px]">
              <div className="p-6 sm:p-8 h-full flex flex-col">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-red-500/10 mb-4">
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Deterministic Risk Detection</h3>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Configurable, rule-based risk checks: TDS mismatches, short deposit, missing PAN
                  compliance, duplicate invoices. Transparent, auditable logic. No black-box decisions.
                </p>
              </div>
            </BentoCard>

            <BentoCard
              colSpan={2}
              glowColor="20, 184, 166"
              className="min-h-[200px]"
            >
              <div className="p-6 sm:p-8 h-full flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-teal-500/10">
                      <Search className="w-5 h-5 text-teal-400" />
                    </div>
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-violet-500/10">
                      <Bot className="w-5 h-5 text-violet-400" />
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">Source-Traceable Evidence & AI Investigation</h3>
                  <p className="text-sm text-slate-400 leading-relaxed max-w-lg">
                    Every finding links to the exact source record with full citations. Investigate with
                    an AI agent that explains outcomes using retrieved evidence — grounded responses,
                    never fabricated.
                  </p>
                </div>
                <div className="flex gap-2 mt-5">
                  <span className="text-[10px] px-2.5 py-1 rounded-full bg-teal-500/10 text-teal-300 font-medium">Citations</span>
                  <span className="text-[10px] px-2.5 py-1 rounded-full bg-teal-500/10 text-teal-300 font-medium">Audit trail</span>
                  <span className="text-[10px] px-2.5 py-1 rounded-full bg-violet-500/10 text-violet-300 font-medium">Grounded AI</span>
                </div>
              </div>
            </BentoCard>
          </BentoGrid>
        </div>
      </section>

      {/* ═══ EVIDENCE / SECURITY ════════════════════════════════════════════════ */}
      <section
        id="evidence"
        className="relative py-16 sm:py-24 border-t border-white/[0.04]"
        aria-labelledby="evidence-heading"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left: headline + description */}
            <motion.div {...fadeUpInView(0)}>
              <h2
                id="evidence-heading"
                className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-4 leading-[1.2]"
              >
                Deterministic where correctness matters.{' '}
                <span className="bg-gradient-to-r from-teal-400 to-blue-400 bg-clip-text text-transparent">
                  AI-assisted where explanation helps.
                </span>
              </h2>
              <p className="text-slate-400 text-sm sm:text-base leading-relaxed mb-8 max-w-md">
                Risk detection is rule-based and fully auditable. The AI layer explains and reasons
                over deterministic outputs — it never determines compliance outcomes or fabricates
                findings.
              </p>
              <Link
                to="/login"
                className="group inline-flex items-center gap-2 px-6 py-3 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-all shadow-lg shadow-blue-600/25 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0B1629]"
              >
                Request Access
                <ArrowRight className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1" />
              </Link>
            </motion.div>

            {/* Right: security point cards */}
            <div id="security" className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {SECURITY_POINTS.map(({ icon: Icon, title, desc }, i) => (
                <motion.div
                  key={title}
                  initial={{ opacity: 0, y: prefersReduced ? 0 : 12 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: '-40px' }}
                  transition={{
                    duration: 0.4,
                    delay: prefersReduced ? 0 : i * 0.08,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                  className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-4 hover:bg-white/[0.05] transition-colors duration-200"
                >
                  <div className="w-8 h-8 rounded-lg bg-teal-500/10 flex items-center justify-center mb-3">
                    <Icon className="w-4 h-4 text-teal-400" />
                  </div>
                  <h3 className="text-sm font-semibold text-white mb-1">{title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ FOOTER ════════════════════════════════════════════════════════════ */}
      <footer className="border-t border-white/[0.04] py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <img src="/app-icon.png" alt="AuditPilot" className="w-5 h-5 rounded object-contain flex-shrink-0" />
            <span className="text-sm font-semibold text-white">AuditPilot</span>
          </div>
          <p className="text-xs text-slate-500 text-center">
            Evidence-backed audit intelligence. Enterprise-grade. Source-traceable.
          </p>
          <Link
            to="/login"
            className="text-xs font-medium text-blue-400 hover:text-blue-300 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 rounded"
          >
            Request Access →
          </Link>
        </div>
      </footer>
    </div>
  )
}
