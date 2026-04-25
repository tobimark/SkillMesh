#!/usr/bin/env python3
"""
Example: Running a skill with SkillMesh.
"""
import asyncio
from skillmesh import ExecutionEngine, ExecutionContext


async def main():
    engine = ExecutionEngine()
    await engine.initialize()

    try:
        # Load skill
        engine.loader.load_skill("examples/example_skill.yaml")

        # Run with variables
        context = ExecutionContext(
            variables={
                "user_name": "Alice",
                "include_farewell": True,
            }
        )

        result = await engine.run("hello_world", context)

        # Print output
        print("\n=== Skill Output ===")
        for step_result in result.results:
            print(f"\n[{step_result.step_name}]")
            print(step_result.output)

    finally:
        await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
