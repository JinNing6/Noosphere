/**
 * Noosphere 类型定义
 */

/** 经验类型 */
export type ExperienceType = 'failure' | 'success' | 'pattern' | 'warning' | 'migration';

/** 经验单元 — 对应 MemoryUnit */
export interface Experience {
  id: string;
  type: ExperienceType;
  framework: string;
  version?: string;
  task_type?: string;
  context?: string;
  observation: string;
  root_cause?: string;
  solution?: string;
  evidence_before?: string;
  evidence_after?: string;
  contributor?: string;
  trust_score: number;
  verified_by: number;
  cited_count: number;
  tags: string[];
  created_at: string;
}

/** 3D 节点（球体上的粒子） */
export interface ParticleData {
  experience: Experience;
  position: [number, number, number];   // 3D 球面坐标
  color: string;
  size: number;
}

/** 统计数据 */
export interface NoosphereStats {
  total_experiences: number;
  active_agents: number;
  frameworks: number;
}
