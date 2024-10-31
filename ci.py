import sys
import random
import anyio
import dagger

async def compile():
  async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
    src = (
      client
      .host()
      .directory(".", exclude=["build/", ".gradle/"])
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
      .directory(".", exclude=["build/", ".gradle/"])
    )
    results = (
      client
      .host()
      .directory(".")
      .with_new_directory("results")
      .directory("./results")
    )
    analysis_container = (
      client
      .container()
      .from_("btnguyen2k/codeql-container")
      .with_directory("/opt/src", src, exclude=[], include=[], owner="codeql:codeql")
      .with_directory("/opt/results", results, exclude=[], include=[], owner="codeql:codeql")
    )
    results_dir = (
      analysis_container
      .with_exec(["security","--override","--language=java","--output=sarif-latest"])
      .directory("/opt/results/")
    )
    await results_dir.export("results/")

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
      .with_exec(["image", "--scanners", "vuln", "--input", "/myImage"])
    )
    trivy_output = await trivy_container.stdout()
    image_ref = await image_container.publish(f"ttl.sh/mytest1-github-12345")
    print(f"Published image to: {image_ref}")

#dagger run python3 ci.py
async def main():
    await compile()
    await codeql_analysis()
    await build_image()

anyio.run(main)
