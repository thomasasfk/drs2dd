using BepInEx;
using BepInEx.Logging;
using Controller;
using CustomEventHandler;
using HarmonyLib;
using UI.Panel;
using UI.SelectPanel;
using UnityEngine;
using UnityEngine.UI;


namespace DanceDashLaunchHelper
{
    [BepInPlugin(PluginInfo.PLUGIN_GUID, PluginInfo.PLUGIN_NAME, PluginInfo.PLUGIN_VERSION)]
    public class Plugin : BaseUnityPlugin
    {
        private void Awake()
        {
            Logger.LogInfo($"Plugin {PluginInfo.PLUGIN_GUID} is loaded!");
            var harmony = new Harmony(PluginInfo.PLUGIN_GUID);
            harmony.PatchAll();
        }
    }

    
    // when we first start the game, we set the ready button to be interactable & click it programmatically
    [HarmonyPatch(typeof(ControllerSwitchUI), "Start")]
    class ControllerSwitchUI_Start_Patch
    {
        static bool Prefix(ControllerSwitchUI __instance)
        {
            Button btn = (Button)Traverse.Create(__instance).Field("readyBTN").GetValue();
            Traverse.Create(btn).Field("m_Interactable").SetValue(true);

            GameObject hintText = (GameObject)Traverse.Create(__instance).Field("hintTextObj").GetValue();
            hintText.SetActive(false);

            btn.onClick.Invoke();
            return true;
        }
    }

    // we trigger PanelGameSetting.OnToggleHpChange with true to force infinite hp (dont wanna die)
    [HarmonyPatch(typeof(PanelGameSetting), "Awake")]
    class PanelGameSetting_Awake_Patch
    {
        static void Postfix(PanelGameSetting __instance)
        {
            Traverse.Create(__instance).Method("OnToggleHpChange", true).GetValue();
        }
    }
    
    // this patch is bad, it hijacks init and toggles the albums and invokes them as true, happens to
    // toggle on the last album (custom songs) purely based on the order of execution, but again, this sucks
    [HarmonyPatch(typeof(VolListItem), "Init")]
    class VolListItem_Init_Patch
    {
        private static ManualLogSource logger = BepInEx.Logging.Logger.CreateLogSource("VolListItem_Init_Patch");

        static void Postfix(VolListItem __instance)
        {
            logger.LogInfo($"Invoking on {__instance} inside VolListItem.Init");
            __instance.Invoke(true);
        }
    }
    
    // hijacks the ost selection happening as a side effect of VolListItem_Init_Patch, and clicks the play button
    [HarmonyPatch(typeof(PanelSelect), "OnSelectOst")]
    class PanelSelect_OnSelectOst_Patch
    {
        static void Postfix(PanelSelect __instance)
        {
            Traverse.Create(__instance).Method("OnClickPlay").GetValue();
        }
    }

    // all of the patches below are purely to avoid errors related to not having a HMD or controllers/trackers
    [HarmonyPatch(typeof(PanelSelect), "OnClickPlay")]
    class PanelSelect_OnClickPlay_Patch
    {
        private static ManualLogSource logger = BepInEx.Logging.Logger.CreateLogSource("PanelSelect_OnClickPlay_Patch");

        static bool Prefix(PanelSelect __instance)
        {
            logger.LogInfo($"Inside prefix of PanelSelect.OnClickPlay");

            // this is copied from the source, with player controller related things excluded (comments)
            PlayerDataManager.Instance.rtr(true);
            if (PlayerDataManager.Instance.IsDRSMode)
                EventHandlerProxy<EvtCenter, dep>.sck(dep.DRSTriggerChange);
            // PlayerController.instance.AllowLaserSwich = false;
            // PlayerController.instance.interactiveControlManagement.rsn();
            SfxManager.tba();
            dhd.tab();
            Traverse.Create(__instance).Method("AddStatByMode").GetValue();
            dhj.tcf("Play");

            return false;
        }
    }

    [HarmonyPatch(typeof(PlayerDataManager), "rtr")]
    class PlayerDataManager_rtr_Patch
    {
        static bool Prefix(PanelSelect __instance, bool a)
        {
            Traverse.Create(__instance).Field("bvxp").SetValue(a);
            return false;
        }
    }

    [HarmonyPatch(typeof(PlayerController), "sze")]
    class PlayerController_sze_Patch
    {
        static bool Prefix(PanelSelect __instance)
        {
            return false;
        }
    }

    [HarmonyPatch(typeof(PlayerController), "syy")]
    class PlayerController_syy_Patch
    {
        static bool Prefix(PanelSelect __instance, deo a)
        {
            return false;
        }
    }

    [HarmonyPatch(typeof(dhj), "tcc")]
    public static class DhjTccPatch
    {
        public static bool Prefix(string a, dhj.dhi[] analyticsParams)
        {
            return false;
        }
    }
    
}