package enguru.shared_ai

default allow := false
default verdict := "BLOCKED"

critical_metadata_known if {
  input.provider.privacy_verified == true
  input.provider.commercial_use_verified == true
  input.provider.cost_verified == true
}

secret_local_only if {
  input.request.data_class != "SECRET"
} else if {
  input.request.data_class == "SECRET"
  input.provider.local == true
}

cost_allowed if {
  input.provider.estimated_cost <= input.request.cost_ceiling
}

capabilities_allowed if {
  every capability in input.request.required_capabilities {
    input.provider.capabilities[capability] == true
  }
}

authority_allowed if {
  input.provider.production_approved == true
}

allow if {
  critical_metadata_known
  secret_local_only
  cost_allowed
  capabilities_allowed
  authority_allowed
  input.provider.health in {"HEALTHY", "DEGRADED"}
}

verdict := "PASS" if allow

verdict := "HOLD" if {
  not allow
  input.provider.candidate == true
  input.provider.production_approved != true
}

# Governance invariant:
# Automated learning/optimization may propose changes but cannot grant
# production approval, paid authority, privacy authority or SECRET egress.
