//window.mywax = new waxjs.WaxJS({rpcEndpoint: 'https://wax.dapplica.io'});

window.sleep = function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

window.wax_login = async function(){
    try {
        const auto_login = await window.mywax.isAutoLoginAvailable();
        if (!auto_login)
            window.mywax.login();
        return [true,"ok"];
    } catch (e){
        return [false, e.message];
    }
}

window.wax_transact = async function(transaction){
    try {
        const auto_login = await window.mywax.isAutoLoginAvailable();
        if (!auto_login){
            await window.mywax.login();
            await window.sleep(3000);
        }
        console.log(transaction)
        const result = await window.mywax.api.transact(transaction, {
                    blocksBehind: 3,
                    expireSeconds: 90,
                });
        return [true, result];
    } catch (e){
        return [false, e.message];
    }
}
