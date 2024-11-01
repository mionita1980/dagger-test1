#dagger run python3 ci.py

import sys
import random
import anyio
import dagger

async def compile():
  async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
    src = (
      client
      .host()
      .directory(".")
    )
    cache = (
      client
      .cache_volume(".gradle")
    )
    build_container = (
      client
      .container()
      .from_("gradle:jdk21")
      .with_directory("/project", src)
      .with_mounted_cache("/project/.gradle",cache)
      .with_workdir("/project")
    )
    build_dir = (
      build_container
      .with_exec(["gradle","test","distTar"])
      .directory("build/")
    )
    await build_dir.export("build/")

async def codeql_analysis():
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        src = (
            client
            .host()
            .directory(".")
        )
        analysis_container = (
            client
            .container()
            .from_("mionita22/codeql-java")
            .with_directory("/project", src, exclude=[], include=[])
            .with_exec(["/run.sh", "/project", "/project/build/codeql-results.sarif"])
        )
        codeql_output = await analysis_container.stdout()
        results_dir = (
            analysis_container
            .directory("/project/build")
        )
        await results_dir.export("build")
    print(f"CodeQL analysis results are in /build/codeql-results.sarif")

async def build_image():
  async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
    src = (
      client
      .host()
      .directory(".")
    )
    image_container = (
      src
      .with_directory("/project", src)
      .docker_build(dockerfile='Dockerfile')
    )
    #ref = await image_container.image_ref()
    exported_file = await image_container.export("/tmp/image.tar")
    print(f"Exported image: {image_container}")
    #docker load -i /tmp/image.tar
    trivy_cache = (
      client
      .cache_volume(".trivy")
    )
    trivy_container = (
      client
      .container()
      .from_("aquasec/trivy:latest")
      .with_mounted_cache("/root/.cache/trivy",trivy_cache)
      .with_mounted_file(f"/myImage", image_container.as_tarball())
      .with_exec(["trivy","image", "--scanners", "vuln", "--input", "/myImage"])
    )
    trivy_output = await trivy_container.stdout()
    image_ref = await image_container.publish(f"ttl.sh/mytest1-github-12345")
    print(f"Published image to: {image_ref}")

#dagger run python3 ci.py
async def main():
    await compile()
    #await codeql_analysis()
    await build_image()

anyio.run(main)
