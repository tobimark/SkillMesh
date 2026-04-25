#!/usr/bin/env python3
"""
SkillMesh CLI - for testing and debugging.
"""
import argparse
import asyncio
from skillmesh import ExecutionEngine, ExecutionContext


async def main():
    parser = argparse.ArgumentParser(description="SkillMesh CLI")
    parser.add_argument("skill", help="Path or URL to skill YAML file")
    parser.add_argument("--var", action="append", help="Variables in key=value format")
    args = parser.parse_args()

    # Parse variables
    variables = {}
    if args.var:
        for var in args.var:
            if "=" in var:
                key, value = var.split("=", 1)
                variables[key] = value

    # Create engine and run skill
    engine = ExecutionEngine()
    await engine.initialize()

    try:
        # Load skill
        skill = engine.loader.load_skill(args.skill)

        # Run skill
        context = ExecutionContext(variables=variables)
        result = await engine.run(skill.name, context)

        # Print results
        print("\n=== Results ===")
        for step_result in result.results:
            print(f"\n[{step_result.step_name}]")
            print(f"Success: {step_result.success}")
            if step_result.success:
                print(f"Output: {step_result.output}")
            else:
                print(f"Error: {step_result.error}")

        print("\n=== Logs ===")
        for log in result.logs:
            print(log)
    finally:
        await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())