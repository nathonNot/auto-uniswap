import json
import sys
import subprocess
import os

config = {}
network_name = ""
v3_factory_address = ""
permit2_address = ""
privateKey = os.getenv("PRIVATE_KEY")

def load_config(file_name):
    global network_name
    global config
    network_name = file_name
    if len(privateKey) < 32:
        raise Exception("PRIVATE_KEY is not set")
    print(f"use key *********{privateKey[:8]} for deploy")
    with open(file_name+".json","r") as f:
        data = f.read()
        config = json.loads(data)
    print(config)
    url = config['url']
    chainId=config["chainId"]
    ## 替换配置模板
    template = f"{network_name}: "+"{"+"\n"
    template += f"      url: '{url}',"+"\n"
    template += f"      chainId: {chainId},"+"\n"
    template += f"      accounts: ['"+f"{privateKey}"+"'],"+"\n"
    if "gas" in config:
        template += f"      gas: {config['gas']},"+"\n"
    if "gasPrice" in config:
        template += f"      gasPrice: {config['gasPrice']},"+"\n"
    template += "    }"
        
    with open("hardhat.config.ts.template","r") as f:
        text = f.read()
        text = text.replace("#network_info#",template)
    with open("v3-core/hardhat.config.ts","w") as f:
        f.write(text)
    with open("v3-periphery/hardhat.config.ts","w") as f:
        f.write(text)
    
def deploy_v3_core():
    # 执行命令行并捕获输出
    current_directory = os.getcwd()

    # 检查当前目录下是否存在 v3-core 目录
    v3_core_directory = os.path.join(current_directory, 'v3-core')
    print(f"deploy v3 core to :{network_name}")
    # 执行命令行并捕获输出
    result = subprocess.run(['npx', 'hardhat', 'run', '--network', network_name, 'scripts/deploy.js'], capture_output=True, text=True, cwd=v3_core_directory)
    # 检查命令是否成功执行
    if result.returncode == 0:
        # 打印命令的标准输出
        print(result.stdout)
        if not os.path.exists(f"deploy_log/{network_name}"):
            os.makedirs(f"deploy_log/{network_name}")
        if not os.path.exists(f"deploy_save"):
            os.makedirs(f"deploy_save")
        with open(f"deploy_log/{network_name}/v3-core.log","w") as f:
            f.write(result.stdout)
        global v3_factory_address
        v3_factory_address = result.stdout.split("Contract deployed to address:")[-1].strip()
        with open(f"deploy_save/{network_name}.save","w") as f:
            f.write(f"v3_factory_address:{v3_factory_address}\n")
    else:
        # 打印错误信息
        print("Command failed with error:")
        raise Exception(result.stderr)


def deploy_v3_periphery():
    with open("periphery_deploy.js.template","r") as f:
        template = f.read()
    eth9_template = "const WWATER = await ethers.getContractFactory('WETH')\n"
    eth9_template += "  const _WWATER = await WWATER.deploy()\n"
    eth9_template += "  wwaterAdr =  _WWATER.address\n"
    eth9_template += "  console.log('WWATER deployed at:', wwaterAdr)\n"
    if "weth9" in config and config["weth9"] != "":
        eth9_address = config["weth9"]
        eth9_template = f"const wwaterAdr = 'eth9_address'"
    template = template.replace("##weth9##",eth9_template)
    template = template.replace("##factoryAdr##", v3_factory_address)
    with open("v3-periphery/scripts/deploy.js","w") as f:
        f.write(template)
    current_directory = os.getcwd()
    # 检查当前目录下是否存在 v3-core 目录
    periphery_directory = os.path.join(current_directory, 'v3-periphery')
    print(f"deploy v3 periphery to :{network_name}")
    # 执行命令行并捕获输出
    result = subprocess.run(['npx', 'hardhat', 'run', '--network', network_name, 'scripts/deploy.js'], capture_output=True, text=True, cwd=periphery_directory)
    # 检查命令是否成功执行
    if result.returncode == 0:
        # 打印命令的标准输出
        print(result.stdout)
        if not os.path.exists(f"deploy_log/{network_name}"):
            os.makedirs(f"deploy_log/{network_name}")
        if not os.path.exists(f"deploy_save"):
            os.makedirs(f"deploy_save")
        with open(f"deploy_log/{network_name}/v3-periphery.log","w") as f:
            f.write(result.stdout)
        deploy_address = result.stdout.split("Successfully generated Typechain artifacts!")[-1].strip()
        with open(f"deploy_save/{network_name}.save","a") as f:
            f.write(deploy_address)
    else:
        # 打印错误信息
        print("Command failed with error:")
        raise Exception(result.stderr)

def deploy_permit2():
    current_directory = os.getcwd()
    # 检查当前目录下是否存在 v3-core 目录
    permit2_directory = os.path.join(current_directory, 'permit2')
    print(f"deploy permit2 to :{network_name}")
    # 执行命令行并捕获输出
    result = subprocess.run([
        'forge', 'create', '--rpc-url', config["url"], 
        '--private-key', privateKey,
        'src/Permit2.sol:Permit2'], capture_output=True, text=True, cwd=permit2_directory)
    # 检查命令是否成功执行
    if result.returncode == 0:
        # 打印命令的标准输出
        print(result.stdout)
        if not os.path.exists(f"deploy_log/{network_name}"):
            os.makedirs(f"deploy_log/{network_name}")
        if not os.path.exists(f"deploy_save"):
            os.makedirs(f"deploy_save")
        with open(f"deploy_log/{network_name}/v3-permit2.log","w") as f:
            f.write(result.stdout)
        deploy_address = result.stdout.split("Deployed to:")[-1].strip()
        deploy_address = deploy_address.split("Transaction hash:")[0].strip()
        global permit2_address
        permit2_address = deploy_address
        with open(f"deploy_save/{network_name}.save","a") as f:
            f.write("\n")
            f.write("permit2 address:" + deploy_address)
    else:
        # 打印错误信息
        print("Command failed with error:")
        raise Exception(result.stderr)

def deploy_route():
    current_directory = os.getcwd()
    eth9_address = ""
    with open(f"deploy_save/{network_name}.save","r") as f:
        for line in f.readlines():
            if "WWATER deployed at" in line:
                eth9_address = line.split("WWATER deployed at:")[-1].strip()
                break    
    if "weth9" in config and config["weth9"] != "":
        eth9_address = config["weth9"]
    with open("DeployWaterfall.s.sol.template","r") as f:
        template = f.read()
    networkUp = ''.join(word.capitalize() for word in network_name.split('_'))
    template = template.replace("##weth9##", eth9_address)
    template = template.replace("##permit2##", permit2_address)
    template = template.replace("##v3Factory##", v3_factory_address)
    template = template.replace("##network##", networkUp)
    d_name = f"Deploy{networkUp}"
    with open(f"universal-router/script/deployParameters/{d_name}.s.sol","w") as f:
        f.write(template)
    route_directory = os.path.join(current_directory, 'universal-router')
    print(f"deploy route to :{network_name}")
    # 执行命令行并捕获输出
    result = subprocess.run(['forge', 'build'],capture_output=True, text=True, cwd=route_directory)
    if result.returncode == 0:
        # 打印命令的标准输出
        print(result.stdout)
    else:
        # 打印错误信息
        raise Exception(result.stderr)
    
    result = subprocess.run([
        'forge', 'script',
        '--broadcast','--rpc-url', config["url"], 
        '--private-key', privateKey,
        '--sig', 'run()',
        f'script/deployParameters/{d_name}.s.sol:{d_name}'],
                            capture_output=True, text=True, cwd=route_directory)
    if result.returncode == 0:
        # 打印命令的标准输出
        print(result.stdout)
        with open(f"deploy_log/{network_name}/universal-router.log","w") as f:
            f.write(result.stdout)
        deploy_address = result.stdout.split("router: contract UniversalRouter")[-1].strip()
        deploy_address = deploy_address.split("== Logs ==")[0].strip()
        with open(f"deploy_save/{network_name}.save","a") as f:
            f.write("\n")
            f.write("UniversalRouter address:" + deploy_address)
    else:
        # 打印错误信息
        raise Exception(result.stderr)
    
        
if __name__ == "__main__":
    file_name = sys.argv[1]
    load_config(file_name)
    deploy_v3_core()
    deploy_v3_periphery()
    deploy_permit2()
    deploy_route()