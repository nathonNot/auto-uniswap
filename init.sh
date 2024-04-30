git submodule update --init --recursive
curl -L https://foundry.paradigm.xyz | bash
cd v3-core
npm install --save-dev hardhat
yarn install
cd ..
cd v3-periphery
npm install --save-dev hardhat
yarn install
cd ..
cd permit2
forge install
cd ..
cd universal-router
npm install --save-dev hardhat
yarn install
forge install
cd ..
# copy deploy file
mkdir v3-core/scripts
mkdir v3-periphery/scripts
cp v3_deploy.js v3-core/scripts/deploy.js
cp weth.sol.template v3-periphery/contracts/lens/WETH.sol