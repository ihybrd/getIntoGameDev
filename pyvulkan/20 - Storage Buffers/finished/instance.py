from config import *
import logging

def supported(extensions, layers):

    """
        ExtensionProperties( std::array<char, VK_MAX_EXTENSION_NAME_SIZE> const & extensionName_ = {},
                           uint32_t                                             specVersion_ = {} )
    """
        
    #check extension support
    supportedExtensions = [extension.extensionName for extension in vkEnumerateInstanceExtensionProperties(None)]

    logging.logger.print("Device can support the following extensions:")
    logging.logger.log_list(supportedExtensions)
    
    for extension in extensions:
        
        if extension in supportedExtensions:
            logging.logger.print(f"Extension \"{extension}\" is supported!")
        else:
            logging.logger.print(f"Extension \"{extension}\" is not supported!")
            return False

    #check layer support
    supportedLayers = [layer.layerName for layer in vkEnumerateInstanceLayerProperties()]

    logging.logger.print("Device can support the following layers:")
    logging.logger.log_list(supportedLayers)

    for layer in layers:
        if layer in supportedLayers:
            logging.logger.print(f"Layer \"{layer}\" is supported!")
        else:
            logging.logger.print(f"Layer \"{layer}\" is not supported!")
            return False

    return True

def make_instance(applicationName):
    logging.logger.print("Making an instance...")

    """
        An instance stores all per-application state info, it is a vulkan handle
        (An opaque integer or pointer value used to refer to a Vulkan object)
    """

    """
        We can scan the system and check which version it will support up to,
        as of vulkan 1.1
        
        VkResult vkEnumerateInstanceVersion(
            uint32_t*                                   pApiVersion);
    """
    version = vkEnumerateInstanceVersion()
    
    logging.logger.print(
        f"System can support vulkan Variant: {version >> 29}\
        , Major: {VK_VERSION_MAJOR(version)}\
        , Minor: {VK_VERSION_MINOR(version)}\
        , Patch: {VK_VERSION_PATCH(version)}"
    )

    """
    We can then either use this version
    (We shoud just be sure to set the patch to 0 for best compatibility/stability)
    """
    version &= ~(0xFFF)

    """
    Or drop down to an earlier version to ensure compatibility with more devices
    VK_MAKE_API_VERSION(major, minor, patch)
    """
    version = VK_MAKE_VERSION(1, 1, 0)

    """
        from _vulkan.py:

        def VkApplicationInfo(
            sType=VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pNext=None,
            pApplicationName=None,
            applicationVersion=None,
            pEngineName=None,
            engineVersion=None,
            apiVersion=None,
        )
    """

    appInfo = VkApplicationInfo(
        pApplicationName = applicationName,
        applicationVersion = version,
        pEngineName = "Doing it the hard way",
        engineVersion = version,
        apiVersion = version
    )

    """
        Everything with Vulkan is "opt-in", so we need to query which extensions glfw needs
        in order to interface with vulkan.
    """
    extensions = glfw.get_required_instance_extensions()
    if is_darwin:
        extensions.append("VK_KHR_portability_enumeration")
        flg = 1
    else:
        flg = None
    if logging.logger.debug_mode:
        extensions.append(VK_EXT_DEBUG_REPORT_EXTENSION_NAME)

    logging.logger.print("extensions to be requested:")
    logging.logger.log_list(extensions)
    
    layers = []
    if logging.logger.debug_mode:
        layers.append("VK_LAYER_KHRONOS_validation")

    supported(extensions, layers)

    """
        from _vulkan.py:

        def VkInstanceCreateInfo(
            sType=VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pNext=None,
            flags=None,
            pApplicationInfo=None,
            enabledLayerCount=None,ppEnabledLayerNames=None,
            enabledExtensionCount=None,ppEnabledExtensionNames=None,
        )
    """
    createInfo = VkInstanceCreateInfo(
        pApplicationInfo = appInfo,
        enabledLayerCount = len(layers), ppEnabledLayerNames = layers, flags=flg,
        enabledExtensionCount = len(extensions), ppEnabledExtensionNames = extensions
    )

    """
        def vkCreateInstance(
            pCreateInfo,
            pAllocator,
            pInstance=None,
        )
        
        throws exception on failure
    """
    try:
        return vkCreateInstance(createInfo, None)
    except:
        logging.logger.print("Failed to create Instance!")
        return None