import type { Hall } from "@/lib/types";
import { SkillCard } from "./SkillCard";

const HALL_IDS = ["sanh-1", "sanh-2", "sanh-3"];

export function SkillHall({ hall, index }: { hall: Hall; index: number }) {
  return (
    <section id={HALL_IDS[index]} className="scroll-mt-20">
      <div className="mb-2">
        <p className="text-xs font-semibold text-coral-500 tracking-widest uppercase mb-1">
          Skill Hall
        </p>
        <div className="flex items-end justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{hall.name}</h2>
            <p className="text-gray-500 text-sm mt-1">{hall.description}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 mt-6">
        {(hall.skills ?? []).map((skill) => (
          <SkillCard key={skill.id} skill={skill} />
        ))}
      </div>
    </section>
  );
}
